package ai.continuum.android.ui.settings

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import ai.continuum.android.data.api.NetworkModule
import ai.continuum.android.data.pref.ContinuumSettings
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class SettingsUiState(
    val serverHost: String = "192.168.1.117",
    val serverPort: Int = 8080,
    val targetRepoPath: String = "/workspace/project",
    val baseBranch: String = "main",
    val cleanCodeEnabled: Boolean = true,
    val archEnabled: Boolean = true,
    val securityEnabled: Boolean = true,
    val perfEnabled: Boolean = true,
    val aiConductEnabled: Boolean = true,
    val passThreshold: Int = 70,
    val vibrationEnabled: Boolean = true,
    val serverAiProvider: String = "gemini",
    val serverAiModel: String = "gemini-3.7-flash",
    val serverSkyBrainActive: Boolean = false,
    val connectionStatus: String = "Not Tested",
    val isTestingConnection: Boolean = false
)

class SettingsViewModel(application: Application) : AndroidViewModel(application) {

    private val context = application.applicationContext

    private val _uiState = MutableStateFlow(
        SettingsUiState(
            serverHost = ContinuumSettings.getServerHost(context),
            serverPort = ContinuumSettings.getServerPort(context),
            targetRepoPath = ContinuumSettings.getTargetRepoPath(context),
            baseBranch = ContinuumSettings.getTargetBaseBranch(context),
            cleanCodeEnabled = ContinuumSettings.isLensEnabled(context, "clean_code"),
            archEnabled = ContinuumSettings.isLensEnabled(context, "clean_architecture"),
            securityEnabled = ContinuumSettings.isLensEnabled(context, "security"),
            perfEnabled = ContinuumSettings.isLensEnabled(context, "performance"),
            aiConductEnabled = ContinuumSettings.isLensEnabled(context, "ai_conduct"),
            passThreshold = ContinuumSettings.getPassThresholdScore(context),
            vibrationEnabled = ContinuumSettings.isVibrationEnabled(context)
        )
    )
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()

    init {
        testConnection()
    }

    fun updateServerConfig(host: String, port: Int) {
        ContinuumSettings.setServerHost(context, host)
        ContinuumSettings.setServerPort(context, port)
        NetworkModule.setBaseUrl("http://$host:$port")
        _uiState.value = _uiState.value.copy(serverHost = host, serverPort = port)
        testConnection()
    }

    fun updateTargetRepo(path: String, branch: String) {
        ContinuumSettings.setTargetRepoPath(context, path)
        ContinuumSettings.setTargetBaseBranch(context, branch)
        _uiState.value = _uiState.value.copy(targetRepoPath = path, baseBranch = branch)
    }

    fun toggleLens(lensKey: String, enabled: Boolean) {
        ContinuumSettings.setLensEnabled(context, lensKey, enabled)
        _uiState.value = when (lensKey) {
            "clean_code" -> _uiState.value.copy(cleanCodeEnabled = enabled)
            "clean_architecture" -> _uiState.value.copy(archEnabled = enabled)
            "security" -> _uiState.value.copy(securityEnabled = enabled)
            "performance" -> _uiState.value.copy(perfEnabled = enabled)
            "ai_conduct" -> _uiState.value.copy(aiConductEnabled = enabled)
            else -> _uiState.value
        }
    }

    fun updatePassThreshold(score: Int) {
        ContinuumSettings.setPassThresholdScore(context, score)
        _uiState.value = _uiState.value.copy(passThreshold = score)
    }

    fun toggleVibration(enabled: Boolean) {
        ContinuumSettings.setVibrationEnabled(context, enabled)
        _uiState.value = _uiState.value.copy(vibrationEnabled = enabled)
    }

    fun testConnection() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isTestingConnection = true, connectionStatus = "Testing...")
            try {
                val res = NetworkModule.apiService.checkHealth()
                if (res.isSuccessful) {
                    val body = res.body()
                    @Suppress("UNCHECKED_CAST")
                    val aiEngine = body?.get("ai_engine") as? Map<String, Any>
                    val provider = aiEngine?.get("provider")?.toString() ?: "gemini"
                    val model = aiEngine?.get("model")?.toString() ?: "gemini-3.8-flash"
                    val skybrainEnabled = aiEngine?.get("skybrain_enabled") as? Boolean ?: false

                    _uiState.value = _uiState.value.copy(
                        isTestingConnection = false,
                        connectionStatus = "Connected (Vibe Server Healthy)",
                        serverAiProvider = provider,
                        serverAiModel = model,
                        serverSkyBrainActive = skybrainEnabled
                    )
                } else {
                    _uiState.value = _uiState.value.copy(
                        isTestingConnection = false,
                        connectionStatus = "Error: HTTP ${res.code()}"
                    )
                }
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isTestingConnection = false,
                    connectionStatus = "Failed: ${e.message}"
                )
            }
        }
    }
}
