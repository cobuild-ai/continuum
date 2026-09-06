package ai.continuum.android.ui.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.continuum.android.data.models.TaskState
import ai.continuum.android.ui.cards.DiffSummaryCard
import ai.continuum.android.ui.cards.LensEvaluationCard
import ai.continuum.android.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    viewModel: ChatViewModel,
    onNavigateToDiff: (String) -> Unit,
    onNavigateToSettings: () -> Unit,
    modifier: Modifier = Modifier
) {
    var promptInput by remember { mutableStateOf("") }
    val uiState by viewModel.uiState.collectAsState()
    val activeTask by viewModel.activeTask.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "🌌 Continuum Vibe",
                            fontWeight = FontWeight.Bold,
                            fontSize = 18.sp,
                            color = TextPrimary
                        )
                        Text(
                            text = "Target: DearTalk-AI [ai/* isolated]",
                            fontSize = 12.sp,
                            color = PrimaryCyan
                        )
                    }
                },
                actions = {
                    IconButton(onClick = onNavigateToSettings) {
                        Text("⚙️", fontSize = 20.sp)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = SurfaceDark)
            )
        },
        bottomBar = {
            Surface(
                color = SurfaceDark,
                modifier = Modifier.fillMaxWidth().navigationBarsPadding().imePadding()
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp)
                ) {
                    TextField(
                        value = promptInput,
                        onValueChange = { promptInput = it },
                        placeholder = { Text("Command Continuum AI...", color = TextMuted) },
                        colors = TextFieldDefaults.colors(
                            focusedContainerColor = SurfaceCard,
                            unfocusedContainerColor = SurfaceCard,
                            focusedTextColor = TextPrimary,
                            unfocusedTextColor = TextPrimary,
                            focusedIndicatorColor = PrimaryCyan,
                            unfocusedIndicatorColor = androidx.compose.ui.graphics.Color.Transparent
                        ),
                        shape = RoundedCornerShape(20.dp),
                        modifier = Modifier.weight(1f)
                    )

                    Spacer(modifier = Modifier.width(8.dp))

                    IconButton(
                        onClick = {
                            if (promptInput.isNotBlank()) {
                                viewModel.sendPrompt(promptInput)
                                promptInput = ""
                            }
                        },
                        colors = IconButtonDefaults.iconButtonColors(containerColor = PrimaryCyan)
                    ) {
                        Icon(Icons.AutoMirrored.Filled.Send, contentDescription = "Send", tint = BackgroundDark)
                    }
                }
            }
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
            // Intro Guide Card
            item {
                Card(
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = SurfaceDark)
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(
                            text = "📱 Deskless Vibe Coding Active",
                            fontWeight = FontWeight.Bold,
                            color = PrimaryCyan,
                            fontSize = 14.sp
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "1. Type prompt ➔ 2. Review 5-Lens Card ➔ 3. Docker Sandbox Runs ➔ 4. One-touch Squash Merge.",
                            color = TextSecondary,
                            fontSize = 12.sp
                        )
                    }
                }
            }

            // Active Task Card Flow
            activeTask?.let { task ->
                item {
                    // User Request Bubble
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.End
                    ) {
                        Surface(
                            shape = RoundedCornerShape(16.dp, 16.dp, 2.dp, 16.dp),
                            color = SurfaceCard,
                            modifier = Modifier.widthIn(max = 280.dp)
                        ) {
                            Text(
                                text = task.prompt,
                                color = TextPrimary,
                                modifier = Modifier.padding(12.dp),
                                fontSize = 14.sp
                            )
                        }
                    }
                }

                // 5-Lens Evaluation Card
                task.lensReport?.let { report ->
                    item {
                        LensEvaluationCard(
                            report = report,
                            onApprove = { viewModel.approveDesign(task.id) },
                            onReject = { viewModel.rejectTask(task.id) },
                            isActionable = task.state == TaskState.AWAITING_DESIGN_APPROVAL
                        )
                    }
                }

                // Diff Ready Card
                task.diffSummary?.let { diff ->
                    item {
                        DiffSummaryCard(
                            diffSummary = diff,
                            onInspectDiff = { onNavigateToDiff(task.id) }
                        )
                    }
                }

                // Merged Status Badge
                if (task.state == TaskState.MERGED) {
                    item {
                        Card(
                            shape = RoundedCornerShape(12.dp),
                            colors = CardDefaults.cardColors(containerColor = PassGreen.copy(alpha = 0.2f)),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier.padding(16.dp)
                            ) {
                                Text(
                                    text = "🎉 Successfully Squash-Merged into main!",
                                    fontWeight = FontWeight.Bold,
                                    color = PassGreen,
                                    fontSize = 15.sp
                                )
                            }
                        }
                    }
                }
            }

            // Loading state
            if (uiState is ChatUiState.Loading) {
                item {
                    Box(modifier = Modifier.fillMaxWidth().padding(16.dp), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator(color = PrimaryCyan)
                    }
                }
            }
        }
    }
}
