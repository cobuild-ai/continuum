package ai.continuum.android.ui.chat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import ai.continuum.android.data.models.DiffSummary
import ai.continuum.android.data.models.ProjectInfo
import ai.continuum.android.data.models.TaskResponse
import ai.continuum.android.data.models.TaskState
import ai.continuum.android.data.repository.TaskRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

sealed class ChatUiState {
    object Idle : ChatUiState()
    object Loading : ChatUiState()
    data class Success(val task: TaskResponse) : ChatUiState()
    data class Error(val message: String) : ChatUiState()
}

class ChatViewModel(
    private val repository: TaskRepository = TaskRepository()
) : ViewModel() {

    private val _uiState = MutableStateFlow<ChatUiState>(ChatUiState.Idle)
    val uiState: StateFlow<ChatUiState> = _uiState.asStateFlow()

    private val _messages = MutableStateFlow<List<ai.continuum.android.data.models.ChatMessage>>(emptyList())
    val messages: StateFlow<List<ai.continuum.android.data.models.ChatMessage>> = _messages.asStateFlow()

    val projects: StateFlow<List<ProjectInfo>> = repository.projects
    val activeProject: StateFlow<ProjectInfo?> = repository.activeProject
    val activeTask: StateFlow<TaskResponse?> = repository.activeTask
    val diffSummary: StateFlow<DiffSummary?> = repository.diffSummary

    init {
        loadProjects()
    }

    fun loadProjects() {
        viewModelScope.launch {
            repository.loadProjects()
        }
    }

    fun selectProject(project: ProjectInfo) {
        viewModelScope.launch {
            _messages.value = emptyList()
            repository.selectProject(project)
        }
    }

    fun sendPrompt(prompt: String, targetRepo: String? = null) {
        if (prompt.isBlank()) return
        val userMsg = ai.continuum.android.data.models.ChatMessage(
            text = prompt,
            isUser = true
        )
        _messages.value = _messages.value + userMsg

        viewModelScope.launch {
            _uiState.value = ChatUiState.Loading
            repository.sendChat(prompt, targetRepo)
                .onSuccess { chatRes ->
                    if (chatRes.isTask && chatRes.task != null) {
                        _uiState.value = ChatUiState.Success(chatRes.task)
                        val agentMsg = ai.continuum.android.data.models.ChatMessage(
                            text = chatRes.reply,
                            isUser = false,
                            task = chatRes.task
                        )
                        _messages.value = _messages.value + agentMsg
                    } else {
                        _uiState.value = ChatUiState.Idle
                        val chatMsg = ai.continuum.android.data.models.ChatMessage(
                            text = chatRes.reply,
                            isUser = false,
                            task = null
                        )
                        _messages.value = _messages.value + chatMsg
                    }
                }
                .onFailure { err ->
                    _uiState.value = ChatUiState.Error(err.message ?: "Unknown error")
                    val errReport = ai.continuum.android.data.models.ChatMessage(
                        text = "⚠️ 통신 오류: ${err.message ?: "서버 응답 없음"}",
                        isUser = false,
                        isError = true,
                        errorMessage = err.message
                    )
                    _messages.value = _messages.value + errReport
                }
        }
    }

    /**
     * Updates the task inside any existing message that references the given taskId.
     * This ensures ChatScreen re-renders with the latest task state (diff, merge status, etc).
     */
    private fun updateTaskInMessages(updatedTask: TaskResponse) {
        _messages.value = _messages.value.map { msg ->
            if (msg.task?.id == updatedTask.id) {
                msg.copy(task = updatedTask)
            } else {
                msg
            }
        }
    }

    fun approveDesign(taskId: String) {
        viewModelScope.launch {
            _uiState.value = ChatUiState.Loading
            repository.approveTask(taskId, approved = true)
                .onSuccess { task ->
                    _uiState.value = ChatUiState.Success(task)
                    // Update existing message with new task data (now includes diffSummary)
                    updateTaskInMessages(task)
                    // Add confirmation message
                    val confirmMsg = ai.continuum.android.data.models.ChatMessage(
                        text = "✅ Design approved. Sandbox execution complete — Diff ready for review.",
                        isUser = false,
                        task = null
                    )
                    _messages.value = _messages.value + confirmMsg
                }
                .onFailure { err ->
                    _uiState.value = ChatUiState.Error(err.message ?: "Approval failed")
                    val errMsg = ai.continuum.android.data.models.ChatMessage(
                        text = "⚠️ 승인 처리 실패: ${err.message ?: "서버 응답 없음"}",
                        isUser = false,
                        isError = true,
                        errorMessage = err.message
                    )
                    _messages.value = _messages.value + errMsg
                }
        }
    }

    fun rejectTask(taskId: String) {
        viewModelScope.launch {
            repository.approveTask(taskId, approved = false, feedback = "Rejected by user")
                .onSuccess { task ->
                    _uiState.value = ChatUiState.Success(task)
                    updateTaskInMessages(task)
                    val rejectMsg = ai.continuum.android.data.models.ChatMessage(
                        text = "🚫 Task [$taskId] rejected by user.",
                        isUser = false
                    )
                    _messages.value = _messages.value + rejectMsg
                }
        }
    }

    fun approveSquashMerge(taskId: String, onMerged: () -> Unit) {
        viewModelScope.launch {
            _uiState.value = ChatUiState.Loading
            repository.approveTask(taskId, approved = true)
                .onSuccess { task ->
                    _uiState.value = ChatUiState.Success(task)
                    updateTaskInMessages(task)
                    if (task.state == TaskState.MERGED) {
                        val mergeMsg = ai.continuum.android.data.models.ChatMessage(
                            text = "🎉 All changes squash-merged into ${task.branchName.substringBefore("/")} successfully!",
                            isUser = false,
                            task = null
                        )
                        _messages.value = _messages.value + mergeMsg
                        onMerged()
                    }
                }
                .onFailure { err ->
                    _uiState.value = ChatUiState.Error(err.message ?: "Merge failed")
                    val errMsg = ai.continuum.android.data.models.ChatMessage(
                        text = "⚠️ 머지 실패: ${err.message ?: "서버 응답 없음"}",
                        isUser = false,
                        isError = true,
                        errorMessage = err.message
                    )
                    _messages.value = _messages.value + errMsg
                }
        }
    }

    fun refreshActiveTask(taskId: String? = null) {
        val targetId = taskId ?: activeTask.value?.id ?: return
        viewModelScope.launch {
            repository.refreshTask(targetId)
                .onSuccess { task ->
                    updateTaskInMessages(task)
                }
        }
    }
}
