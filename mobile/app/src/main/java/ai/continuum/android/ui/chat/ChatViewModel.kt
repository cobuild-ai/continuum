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
            repository.createTask(prompt, targetRepo)
                .onSuccess { task ->
                    _uiState.value = ChatUiState.Success(task)
                    val agentMsg = ai.continuum.android.data.models.ChatMessage(
                        text = "Task [${task.id}] 시작: ${task.prompt}",
                        isUser = false,
                        task = task
                    )
                    _messages.value = _messages.value + agentMsg
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

    fun approveDesign(taskId: String) {
        viewModelScope.launch {
            _uiState.value = ChatUiState.Loading
            repository.approveTask(taskId, approved = true)
                .onSuccess { task ->
                    _uiState.value = ChatUiState.Success(task)
                }
                .onFailure { err ->
                    _uiState.value = ChatUiState.Error(err.message ?: "Approval failed")
                }
        }
    }

    fun rejectTask(taskId: String) {
        viewModelScope.launch {
            repository.approveTask(taskId, approved = false, feedback = "Rejected by user")
                .onSuccess { task ->
                    _uiState.value = ChatUiState.Success(task)
                }
        }
    }

    fun approveSquashMerge(taskId: String, onMerged: () -> Unit) {
        viewModelScope.launch {
            _uiState.value = ChatUiState.Loading
            repository.approveTask(taskId, approved = true)
                .onSuccess { task ->
                    _uiState.value = ChatUiState.Success(task)
                    if (task.state == TaskState.MERGED) {
                        onMerged()
                    }
                }
                .onFailure { err ->
                    _uiState.value = ChatUiState.Error(err.message ?: "Merge failed")
                }
        }
    }

    fun refreshActiveTask(taskId: String? = null) {
        val targetId = taskId ?: activeTask.value?.id ?: return
        viewModelScope.launch {
            repository.refreshTask(targetId)
        }
    }
}
