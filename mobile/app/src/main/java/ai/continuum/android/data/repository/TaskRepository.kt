package ai.continuum.android.data.repository

import ai.continuum.android.data.api.NetworkModule
import ai.continuum.android.data.models.ApprovalRequest
import ai.continuum.android.data.models.DiffSummary
import ai.continuum.android.data.models.TaskCreateRequest
import ai.continuum.android.data.models.TaskResponse
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class TaskRepository {

    private val api = NetworkModule.apiService

    private val _activeTask = MutableStateFlow<TaskResponse?>(null)
    val activeTask: StateFlow<TaskResponse?> = _activeTask.asStateFlow()

    private val _diffSummary = MutableStateFlow<DiffSummary?>(null)
    val diffSummary: StateFlow<DiffSummary?> = _diffSummary.asStateFlow()

    suspend fun createTask(prompt: String, targetRepo: String? = null): Result<TaskResponse> {
        return try {
            val res = api.createTask(TaskCreateRequest(prompt = prompt, targetRepoPath = targetRepo))
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
