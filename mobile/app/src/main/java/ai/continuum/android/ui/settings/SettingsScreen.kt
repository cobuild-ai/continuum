package ai.continuum.android.ui.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.continuum.android.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    viewModel: SettingsViewModel,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val state by viewModel.uiState.collectAsState()

    var hostInput by remember(state.serverHost) { mutableStateOf(state.serverHost) }
    var portInput by remember(state.serverPort) { mutableStateOf(state.serverPort.toString()) }
    var repoPathInput by remember(state.targetRepoPath) { mutableStateOf(state.targetRepoPath) }
    var branchInput by remember(state.baseBranch) { mutableStateOf(state.baseBranch) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "⚙️ Continuum Settings",
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = PrimaryCyan)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = SurfaceDark)
            )
        },
        containerColor = BackgroundDark,
        modifier = modifier.fillMaxSize()
    ) { paddingValues ->
        LazyColumn(
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Section 1: Server Connection
            item {
                SettingsSectionCard(title = "🌐 Vibe Server Host Connection") {
                    OutlinedTextField(
                        value = hostInput,
                        onValueChange = {
                            hostInput = it
                            viewModel.updateServerConfig(it, portInput.toIntOrNull() ?: 8080)
                        },
                        label = { Text("Host Address (IP / Domain)") },
                        modifier = Modifier.fillMaxWidth()
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    OutlinedTextField(
                        value = portInput,
                        onValueChange = {
                            portInput = it
                            viewModel.updateServerConfig(hostInput, it.toIntOrNull() ?: 8080)
                        },
                        label = { Text("Port (Default: 8080)") },
                        modifier = Modifier.fillMaxWidth()
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = state.connectionStatus,
                            color = if (state.connectionStatus.startsWith("Connected")) PassGreen else TextMuted,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium
                        )

                        Button(
                            onClick = { viewModel.testConnection() },
                            colors = ButtonDefaults.buttonColors(containerColor = PrimaryCyan),
                            enabled = !state.isTestingConnection
                        ) {
                            if (state.isTestingConnection) {
                                CircularProgressIndicator(modifier = Modifier.size(16.dp), color = BackgroundDark)
                            } else {
                                Icon(Icons.Default.Refresh, contentDescription = null, tint = BackgroundDark, modifier = Modifier.size(16.dp))
                                Spacer(modifier = Modifier.width(4.dp))
                                Text("Test Ping", color = BackgroundDark, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }

            // Section 2: Target Project
            item {
                SettingsSectionCard(title = "🌿 Managed Target Project") {
                    OutlinedTextField(
                        value = repoPathInput,
                        onValueChange = {
                            repoPathInput = it
                            viewModel.updateTargetRepo(it, branchInput)
                        },
                        label = { Text("Target Repo Absolute Path") },
                        modifier = Modifier.fillMaxWidth()
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    OutlinedTextField(
                        value = branchInput,
                        onValueChange = {
                            branchInput = it
                            viewModel.updateTargetRepo(repoPathInput, it)
                        },
                        label = { Text("Base Branch (e.g. main)") },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }

            // Section 3: SkyBrain 5-Lens Quality Guard
            item {
                SettingsSectionCard(title = "🔍 SkyBrain 5-Lens Quality Guard") {
                    LensToggleRow("Clean Code Lens", state.cleanCodeEnabled) {
                        viewModel.toggleLens("clean_code", it)
                    }
                    LensToggleRow("Clean Architecture Lens", state.archEnabled) {
                        viewModel.toggleLens("clean_architecture", it)
                    }
                    LensToggleRow("Security Lens (OWASP)", state.securityEnabled) {
                        viewModel.toggleLens("security", it)
                    }
                    LensToggleRow("Performance Lens", state.perfEnabled) {
                        viewModel.toggleLens("performance", it)
                    }
                    LensToggleRow("AI Conduct Lens (Zero Fake)", state.aiConductEnabled) {
                        viewModel.toggleLens("ai_conduct", it)
                    }

                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = "Pass Threshold Score: ${state.passThreshold} / 100",
                        fontSize = 13.sp,
                        color = TextPrimary,
                        fontWeight = FontWeight.SemiBold
                    )
                    Slider(
                        value = state.passThreshold.toFloat(),
                        onValueChange = { viewModel.updatePassThreshold(it.toInt()) },
                        valueRange = 50f..95f,
                        steps = 8,
                        colors = SliderDefaults.colors(thumbColor = PrimaryCyan, activeTrackColor = PrimaryCyan)
                    )
                }
            }

            // Section 4: Server AI Engine Status (View Only)
            item {
                SettingsSectionCard(title = "🤖 Server AI Engine (View Only)") {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column {
                            Text(
                                text = "Active Cloud Provider",
                                fontSize = 12.sp,
                                color = TextSecondary
                            )
                            Text(
                                text = state.serverAiProvider.uppercase(),
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = TextPrimary
                            )
                        }
                        Surface(
                            shape = RoundedCornerShape(6.dp),
                            color = PrimaryCyan.copy(alpha = 0.15f),
                            border = androidx.compose.foundation.BorderStroke(0.5.dp, PrimaryCyan)
                        ) {
                            Text(
                                text = "⚡ ${state.serverAiModel}",
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                color = PrimaryCyan,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = "Local SkyBrain SLM",
                            fontSize = 13.sp,
                            color = TextPrimary
                        )
                        Text(
                            text = if (state.serverSkyBrainActive) "Active (qwen3.8)" else "Disabled (Cloud Only)",
                            fontSize = 12.sp,
                            color = if (state.serverSkyBrainActive) PassGreen else TextMuted,
                            fontWeight = FontWeight.Medium
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "🔒 AI 엔진(Gemini, Claude, Codex 등) 및 API Key는 서버의 `.env` 파일에서 안전하게 설정되며 클라이언트는 자동 감지하여 표시합니다.",
                        fontSize = 11.sp,
                        color = TextMuted
                    )
                }
            }

            // Section 5: Feedback & Governance
            item {
                SettingsSectionCard(title = "🔔 Feedback & Governance") {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(text = "Haptic Vibration on Push", color = TextPrimary)
                        Switch(
                            checked = state.vibrationEnabled,
                            onCheckedChange = { viewModel.toggleVibration(it) }
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "🏛️ Enterprise Governance: Truth-First Protocol & Zero Cloud Token via Local SkyBrain SLM.",
                        fontSize = 11.sp,
                        color = TextMuted
                    )
                }
            }
        }
    }
}

@Composable
fun SettingsSectionCard(title: String, content: @Composable ColumnScope.() -> Unit) {
    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = title,
                fontWeight = FontWeight.Bold,
                fontSize = 15.sp,
                color = PrimaryCyan
            )
            Spacer(modifier = Modifier.height(12.dp))
            content()
        }
    }
}

@Composable
fun LensToggleRow(title: String, enabled: Boolean, onToggle: (Boolean) -> Unit) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween,
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp)
    ) {
        Text(text = title, fontSize = 13.sp, color = TextPrimary)
        Switch(
            checked = enabled,
            onCheckedChange = onToggle,
            colors = SwitchDefaults.colors(checkedThumbColor = PrimaryCyan)
        )
    }
}
