package ai.continuum.android

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import ai.continuum.android.ui.chat.ChatScreen
import ai.continuum.android.ui.chat.ChatViewModel
import ai.continuum.android.ui.diff.DiffViewerScreen
import ai.continuum.android.ui.settings.SettingsScreen
import ai.continuum.android.ui.settings.SettingsViewModel
import ai.continuum.android.ui.theme.ContinuumTheme

class MainActivity : ComponentActivity() {

    private val chatViewModel: ChatViewModel by viewModels()
    private val settingsViewModel: SettingsViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize API base URL dynamically from persistent settings (Zero Hardcoded IP)
        ai.continuum.android.data.api.NetworkModule.setBaseUrl(ai.continuum.android.data.pref.ContinuumSettings.getServerUrl(this))

        handleIntent(intent)

        setContent {
            ContinuumTheme {
                val navController = rememberNavController()

                NavHost(navController = navController, startDestination = "chat") {
                    composable("chat") {
                        ChatScreen(
                            viewModel = chatViewModel,
                            onNavigateToDiff = { taskId ->
                                navController.navigate("diff/$taskId")
                            },
                            onNavigateToSettings = {
                                navController.navigate("settings")
                            }
                        )
                    }

                    composable("diff/{taskId}") { backStackEntry ->
                        val taskId = backStackEntry.arguments?.getString("taskId") ?: ""
                        DiffViewerScreen(
                            taskId = taskId,
                            viewModel = chatViewModel,
                            onNavigateBack = {
                                navController.popBackStack()
                            }
                        )
                    }

                    composable("settings") {
                        SettingsScreen(
                            viewModel = settingsViewModel,
                            onNavigateBack = {
                                navController.popBackStack()
                            }
                        )
                    }
                }
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent?) {
        val uri = intent?.data ?: return
        val pathSegments = uri.pathSegments
        if (pathSegments.isNotEmpty()) {
            val taskId = pathSegments.first()
            chatViewModel.refreshActiveTask(taskId)
        }
    }
}
