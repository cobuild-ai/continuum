package ai.continuum.android.data.pref

import android.content.Context
import android.content.SharedPreferences

object ContinuumSettings {
    private const val PREF_NAME = "continuum_preferences"

    // Server connection
    private const val KEY_SERVER_HOST = "key_server_host"
    private const val KEY_SERVER_PORT = "key_server_port"

    // Target Project
    private const val KEY_TARGET_REPO_PATH = "key_target_repo_path"
    private const val KEY_TARGET_BASE_BRANCH = "key_target_base_branch"
    private const val KEY_AI_BRANCH_PREFIX = "key_ai_branch_prefix"

    // 5-Lens Sensitivity & Activation
    private const val KEY_LENS_CLEAN_CODE_ENABLED = "key_lens_clean_code_enabled"
    private const val KEY_LENS_ARCH_ENABLED = "key_lens_arch_enabled"
    private const val KEY_LENS_SECURITY_ENABLED = "key_lens_security_enabled"
    private const val KEY_LENS_PERFORMANCE_ENABLED = "key_lens_performance_enabled"
    private const val KEY_LENS_AI_CONDUCT_ENABLED = "key_lens_ai_conduct_enabled"
    private const val KEY_PASS_THRESHOLD_SCORE = "key_pass_threshold_score"

    // Docker Sandbox
    private const val KEY_DOCKER_IMAGE = "key_docker_image"
    private const val KEY_SANDBOX_TIMEOUT_SEC = "key_sandbox_timeout_sec"
    private const val KEY_ALLOW_LOCAL_FALLBACK = "key_allow_local_fallback"

    // Notification
    private const val KEY_NOTIFY_LENS_COMPLETE = "key_notify_lens_complete"
    private const val KEY_NOTIFY_DIFF_READY = "key_notify_diff_ready"
    private const val KEY_VIBRATION_ENABLED = "key_vibration_enabled"

    // Language
    private const val KEY_LANGUAGE_CODE = "key_language_code"

    private fun getPrefs(context: Context): SharedPreferences {
        return context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
    }

    // Server
    fun getServerUrl(context: Context): String {
        val host = getPrefs(context).getString(KEY_SERVER_HOST, "192.168.1.117") ?: "192.168.1.117"
        val port = getPrefs(context).getInt(KEY_SERVER_PORT, 8080)
        return "http://$host:$port"
    }

    fun getServerHost(context: Context): String = getPrefs(context).getString(KEY_SERVER_HOST, "192.168.1.117") ?: "192.168.1.117"
    fun setServerHost(context: Context, host: String) = getPrefs(context).edit().putString(KEY_SERVER_HOST, host).apply()

    fun getServerPort(context: Context): Int = getPrefs(context).getInt(KEY_SERVER_PORT, 8080)
    fun setServerPort(context: Context, port: Int) = getPrefs(context).edit().putInt(KEY_SERVER_PORT, port).apply()

    // Target Repo
    fun getTargetRepoPath(context: Context): String =
        getPrefs(context).getString(KEY_TARGET_REPO_PATH, "/Users/smilelife/Projects/OSSProject/01-production/deartalk-ai") ?: "/Users/smilelife/Projects/OSSProject/01-production/deartalk-ai"
    fun setTargetRepoPath(context: Context, path: String) = getPrefs(context).edit().putString(KEY_TARGET_REPO_PATH, path).apply()

    fun getTargetBaseBranch(context: Context): String =
        getPrefs(context).getString(KEY_TARGET_BASE_BRANCH, "main") ?: "main"
    fun setTargetBaseBranch(context: Context, branch: String) = getPrefs(context).edit().putString(KEY_TARGET_BASE_BRANCH, branch).apply()

    fun getAiBranchPrefix(context: Context): String =
        getPrefs(context).getString(KEY_AI_BRANCH_PREFIX, "ai/") ?: "ai/"

    // 5 Lenses
    fun isLensEnabled(context: Context, lensKey: String): Boolean {
        val prefKey = when (lensKey) {
            "clean_code" -> KEY_LENS_CLEAN_CODE_ENABLED
            "clean_architecture" -> KEY_LENS_ARCH_ENABLED
            "security" -> KEY_LENS_SECURITY_ENABLED
            "performance" -> KEY_LENS_PERFORMANCE_ENABLED
            "ai_conduct" -> KEY_LENS_AI_CONDUCT_ENABLED
            else -> return true
        }
        return getPrefs(context).getBoolean(prefKey, true)
    }

    fun setLensEnabled(context: Context, lensKey: String, enabled: Boolean) {
        val prefKey = when (lensKey) {
            "clean_code" -> KEY_LENS_CLEAN_CODE_ENABLED
            "clean_architecture" -> KEY_LENS_ARCH_ENABLED
            "security" -> KEY_LENS_SECURITY_ENABLED
            "performance" -> KEY_LENS_PERFORMANCE_ENABLED
            "ai_conduct" -> KEY_LENS_AI_CONDUCT_ENABLED
            else -> return
        }
        getPrefs(context).edit().putBoolean(prefKey, enabled).apply()
    }

    fun getPassThresholdScore(context: Context): Int = getPrefs(context).getInt(KEY_PASS_THRESHOLD_SCORE, 70)
    fun setPassThresholdScore(context: Context, score: Int) = getPrefs(context).edit().putInt(KEY_PASS_THRESHOLD_SCORE, score).apply()

    // Notifications
    fun isNotifyDiffReady(context: Context): Boolean = getPrefs(context).getBoolean(KEY_NOTIFY_DIFF_READY, true)
    fun setNotifyDiffReady(context: Context, enabled: Boolean) = getPrefs(context).edit().putBoolean(KEY_NOTIFY_DIFF_READY, enabled).apply()

    fun isVibrationEnabled(context: Context): Boolean = getPrefs(context).getBoolean(KEY_VIBRATION_ENABLED, true)
    fun setVibrationEnabled(context: Context, enabled: Boolean) = getPrefs(context).edit().putBoolean(KEY_VIBRATION_ENABLED, enabled).apply()

    // Language
    fun getLanguageCode(context: Context): String = getPrefs(context).getString(KEY_LANGUAGE_CODE, "auto") ?: "auto"
    fun setLanguageCode(context: Context, code: String) = getPrefs(context).edit().putString(KEY_LANGUAGE_CODE, code).apply()
}
