package ai.continuum.android.data.repository

import ai.continuum.android.data.api.NetworkModule
import ai.continuum.android.data.models.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class TaskRepository {

    private val api = NetworkModule.apiService

    private val _projects = MutableStateFlow<List<ProjectInfo>>(emptyList())
    val projects: StateFlow<List<ProjectInfo>> = _projects.asStateFlow()

    private val _activeProject = MutableStateFlow<ProjectInfo?>(null)
    val activeProject: StateFlow<ProjectInfo?> = _activeProject.asStateFlow()

    private val _activeTask = MutableStateFlow<TaskResponse?>(null)
    val activeTask: StateFlow<TaskResponse?> = _activeTask.asStateFlow()

    private val _diffSummary = MutableStateFlow<DiffSummary?>(null)
    val diffSummary: StateFlow<DiffSummary?> = _diffSummary.asStateFlow()

    suspend fun loadProjects(): Result<List<ProjectInfo>> {
        return try {
            val res = api.listProjects()
            if (res.isSuccessful && res.body() != null) {
                _projects.value = res.body()!!
                if (_activeProject.value == null && res.body()!!.isNotEmpty()) {
                    _activeProject.value = res.body()!!.first()
                }
                Result.success(res.body()!!)
            } else {
                val fallback = listOf(
                    ProjectInfo("deartalk-ai", "/Users/smilelife/Projects/OSSProject/01-production/deartalk-ai", "main", true, true, "On-device AI chat app"),
                    ProjectInfo("skybrain", "/Users/smilelife/Projects/OSSProject/01-production/skybrain", "main", true, true, "Local SLM serving daemon"),
                    ProjectInfo("continuum", "/Users/smilelife/Projects/OSSProject/01-production/continuum", "main", true, true, "Vibe server & mobile client"),
                    ProjectInfo("skynexus", "/Users/smilelife/Projects/OSSProject/01-production/skynexus", "main", true, true, "Gateway orchestrator"),
                    ProjectInfo("myskynet", "/Users/smilelife/Projects/OSSProject/01-production/myskynet", "main", true, true, "Cloud coordination")
                )
                _projects.value = fallback
                if (_activeProject.value == null) _activeProject.value = fallback.first()
                Result.success(fallback)
            }
        } catch (e: Exception) {
            val fallback = listOf(
                ProjectInfo("deartalk-ai", "/Users/smilelife/Projects/OSSProject/01-production/deartalk-ai", "main", true, true, "On-device AI chat app"),
                ProjectInfo("skybrain", "/Users/smilelife/Projects/OSSProject/01-production/skybrain", "main", true, true, "Local SLM serving daemon"),
                ProjectInfo("continuum", "/Users/smilelife/Projects/OSSProject/01-production/continuum", "main", true, true, "Vibe server & mobile client")
            )
            _projects.value = fallback
            if (_activeProject.value == null) _activeProject.value = fallback.first()
            Result.success(fallback)
        }
    }

    suspend fun selectProject(project: ProjectInfo): Result<ProjectInfo> {
        _activeProject.value = project
        _activeTask.value = null
        _diffSummary.value = null
        return try {
            val res = api.selectProject(ProjectSelectRequest(project.path))
            if (res.isSuccessful && res.body() != null) {
                _activeProject.value = res.body()
                Result.success(res.body()!!)
            } else {
                Result.success(project)
            }
        } catch (e: Exception) {
            Result.success(project)
        }
    }

    suspend fun sendChat(message: String, targetRepo: String? = null): Result<ChatResponse> {
        return try {
            val repo = targetRepo ?: _activeProject.value?.path
            val res = api.chatWithAgent(ChatRequest(message = message, targetRepoPath = repo))
            if (res.isSuccessful && res.body() != null) {
                val chatRes = res.body()!!
                if (chatRes.isTask && chatRes.task != null) {
                    _activeTask.value = chatRes.task
                }
                Result.success(chatRes)
            } else {
                // Fallback to direct task creation if chat endpoint returns error
                val fallbackTaskRes = createTask(message, repo)
                if (fallbackTaskRes.isSuccess) {
                    val task = fallbackTaskRes.getOrNull()!!
                    Result.success(ChatResponse(
                        reply = "🛠️ 코드 구현 태스크가 접수되었습니다.",
                        isTask = true,
                        task = task
                    ))
                } else {
                    Result.failure(Exception("Chat failed: ${res.code()}"))
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun loadChatHistory(projectPath: String? = null): Result<List<ChatMessage>> {
        return try {
            val target = projectPath ?: _activeProject.value?.path
            val res = api.getChatHistory(target)
            if (res.isSuccessful && res.body() != null) {
                Result.success(res.body()!!)
            } else {
                Result.success(emptyList())
            }
        } catch (e: Exception) {
            Result.success(emptyList())
        }
    }

    suspend fun clearChatHistory(projectPath: String? = null): Result<Boolean> {
        return try {
            val target = projectPath ?: _activeProject.value?.path
            val res = api.clearChatHistory(target)
            Result.success(res.isSuccessful)
        } catch (e: Exception) {
            Result.success(false)
        }
    }

    suspend fun createTask(prompt: String, targetRepo: String? = null): Result<TaskResponse> {
        return try {
            val repo = targetRepo ?: _activeProject.value?.path
            val res = api.createTask(TaskCreateRequest(prompt = prompt, targetRepoPath = repo))
            if (res.isSuccessful && res.body() != null) {
                _activeTask.value = res.body()
                Result.success(res.body()!!)
            } else {
                Result.failure(Exception("Failed to create task: ${res.code()} ${res.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun refreshTask(taskId: String): Result<TaskResponse> {
        return try {
            val res = api.getTask(taskId)
            if (res.isSuccessful && res.body() != null) {
                _activeTask.value = res.body()
                Result.success(res.body()!!)
            } else {
                Result.failure(Exception("Failed to fetch task: ${res.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun approveTask(taskId: String, approved: Boolean, feedback: String? = null): Result<TaskResponse> {
        return try {
            val res = api.approveTask(taskId, ApprovalRequest(approved = approved, feedback = feedback))
            if (res.isSuccessful && res.body() != null) {
                val updated = res.body()!!
                _activeTask.value = updated
                if (updated.diffSummary != null) {
                    _diffSummary.value = updated.diffSummary
                }
                Result.success(updated)
            } else {
                Result.failure(Exception("Approval request failed: ${res.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchDiff(taskId: String): Result<DiffSummary> {
        return try {
            val res = api.getTaskDiff(taskId)
            if (res.isSuccessful && res.body() != null) {
                _diffSummary.value = res.body()
                Result.success(res.body()!!)
            } else {
                Result.failure(Exception("Failed to fetch diff: ${res.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
