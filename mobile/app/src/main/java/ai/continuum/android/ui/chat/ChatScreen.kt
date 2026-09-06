package ai.continuum.android.ui.chat

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
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
    var thoughtExpanded by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            Surface(
                color = BackgroundDark,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier
                        .statusBarsPadding()
                        .padding(horizontal = 16.dp, vertical = 8.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column {
                            Text(
                                text = "Agent",
                                fontSize = 12.sp,
                                color = TextSecondary,
                                fontWeight = FontWeight.Medium
                            )
                            Text(
                                text = activeTask?.prompt?.take(32)?.let { if (activeTask!!.prompt.length > 32) "$it..." else it }
                                    ?: "Continuum Coding Session",
                                fontWeight = FontWeight.SemiBold,
                                fontSize = 15.sp,
                                color = TextPrimary,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }

                        // Action Icons: Refresh, Settings, New Task
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            IconButton(onClick = { viewModel.refreshActiveTask() }) {
                                Icon(Icons.Default.Refresh, contentDescription = "Refresh", tint = TextSecondary, modifier = Modifier.size(18.dp))
                            }
                            IconButton(onClick = onNavigateToSettings) {
                                Icon(Icons.Default.Settings, contentDescription = "Settings", tint = TextSecondary, modifier = Modifier.size(18.dp))
                            }
                        }
                    }
                    HorizontalDivider(color = CardBorder, thickness = 0.5.dp, modifier = Modifier.padding(top = 8.dp))
                }
            }
        },
        bottomBar = {
            Surface(
                color = BackgroundDark,
                modifier = Modifier
                    .fillMaxWidth()
                    .navigationBarsPadding()
                    .imePadding()
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 12.dp, vertical = 8.dp)
                ) {
                    // Modern IDE Input Box
                    Card(
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceCard),
                        modifier = Modifier
                            .fillMaxWidth()
                            .border(1.dp, CardBorder, RoundedCornerShape(16.dp))
                    ) {
                        Column(modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp)) {
                            // Text Input Field
                            TextField(
                                value = promptInput,
                                onValueChange = { promptInput = it },
                                placeholder = {
                                    Text(
                                        "Ask anything, @ to mention, / for actions",
                                        color = TextMuted,
                                        fontSize = 13.sp
                                    )
                                },
                                colors = TextFieldDefaults.colors(
                                    focusedContainerColor = androidx.compose.ui.graphics.Color.Transparent,
                                    unfocusedContainerColor = androidx.compose.ui.graphics.Color.Transparent,
                                    focusedTextColor = TextPrimary,
                                    unfocusedTextColor = TextPrimary,
                                    focusedIndicatorColor = androidx.compose.ui.graphics.Color.Transparent,
                                    unfocusedIndicatorColor = androidx.compose.ui.graphics.Color.Transparent
                                ),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .heightIn(min = 40.dp, max = 100.dp)
                            )

                            Spacer(modifier = Modifier.height(6.dp))

                            // Bottom Controls inside Input Card
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.SpaceBetween,
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(
                                        imageVector = Icons.Default.Add,
                                        contentDescription = "Add attachment",
                                        tint = TextMuted,
                                        modifier = Modifier.size(18.dp)
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))

                                    // Model Switcher Pill
                                    Surface(
                                        shape = RoundedCornerShape(6.dp),
                                        color = IDETagBg,
                                        modifier = Modifier.clip(RoundedCornerShape(6.dp))
                                    ) {
                                        Row(
                                            verticalAlignment = Alignment.CenterVertically,
                                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                        ) {
                                            Text(
                                                text = "⚡ SkyBrain (Qwen 3.8) ➔ Lead Gemini",
                                                color = TextSecondary,
                                                fontSize = 11.sp,
                                                fontWeight = FontWeight.Medium
                                            )
                                            Spacer(modifier = Modifier.width(4.dp))
                                            Icon(
                                                imageVector = Icons.Default.KeyboardArrowDown,
                                                contentDescription = null,
                                                tint = TextSecondary,
                                                modifier = Modifier.size(12.dp)
                                            )
                                        }
                                    }
                                }

                                // Send Button
                                IconButton(
                                    onClick = {
                                        if (promptInput.isNotBlank()) {
                                            viewModel.sendPrompt(promptInput)
                                            promptInput = ""
                                        }
                                    },
                                    colors = IconButtonDefaults.iconButtonColors(containerColor = IDEButtonBlue),
                                    modifier = Modifier.size(28.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.AutoMirrored.Filled.Send,
                                        contentDescription = "Send",
                                        tint = TextPrimary,
                                        modifier = Modifier.size(14.dp)
                                    )
                                }
                            }
                        }
                    }
                }
            }
        },
        containerColor = BackgroundDark,
        modifier = modifier.fillMaxSize()
    ) { paddingValues ->
        LazyColumn(
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Pill Badge: Proceeded with Implementation Plan
            item {
                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = SurfaceCard,
                    modifier = Modifier.border(1.dp, CardBorder, RoundedCornerShape(20.dp))
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = null,
                            tint = PassGreen,
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Proceeded with",
                            color = TextSecondary,
                            fontSize = 12.sp
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Icon(
                            imageVector = Icons.Default.Description,
                            contentDescription = null,
                            tint = TextPrimary,
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "Implementation Plan",
                            color = TextPrimary,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
            }

            // Thought step badge (Collapsible)
            item {
                Column(modifier = Modifier.fillMaxWidth()) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier
                            .clip(RoundedCornerShape(6.dp))
                            .clickable { thoughtExpanded = !thoughtExpanded }
                            .padding(vertical = 4.dp)
                    ) {
                        Text(
                            text = "Thought for 1.2s",
                            color = TextSecondary,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Medium
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Icon(
                            imageVector = if (thoughtExpanded) Icons.Default.KeyboardArrowDown else Icons.Default.ChevronRight,
                            contentDescription = null,
                            tint = TextSecondary,
                            modifier = Modifier.size(14.dp)
                        )
                    }

                    AnimatedVisibility(visible = thoughtExpanded) {
                        Surface(
                            shape = RoundedCornerShape(8.dp),
                            color = SurfaceCard,
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 6.dp)
                                .border(0.5.dp, CardBorder, RoundedCornerShape(8.dp))
                        ) {
                            Column(modifier = Modifier.padding(10.dp)) {
                                Text(
                                    text = "⚡ SkyBrain 5-Lens Evaluation: CleanCode 95/100, Architecture 90/100, Security 100/100, Performance 92/100, AIConduct 100/100. Target branch ai/task ready.",
                                    color = TextSecondary,
                                    fontSize = 11.sp,
                                    fontFamily = FontFamily.Monospace
                                )
                            }
                        }
                    }
                }
            }

            // Active Task Flow
            activeTask?.let { task ->
                // Activity Link: Edited file
                item {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "Edited",
                            color = TextSecondary,
                            fontSize = 13.sp
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(text = "🐍", fontSize = 12.sp)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "test_e2e_workflow.py",
                            color = TextPrimary,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "+76",
                            color = DiffAdditionText,
                            fontSize = 12.sp,
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "-0",
                            color = DiffDeletionText,
                            fontSize = 12.sp,
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }

                // Command Link: Ran 2 commands
                item {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(vertical = 2.dp)
                    ) {
                        Text(
                            text = "Ran 2 commands",
                            color = TextSecondary,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Medium
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Icon(
                            imageVector = Icons.Default.ChevronRight,
                            contentDescription = null,
                            tint = TextSecondary,
                            modifier = Modifier.size(14.dp)
                        )
                    }
                }

                // HERO SECTION: 7 Files With Changes Card
                item {
                    val summary = task.diffSummary ?: ai.continuum.android.data.models.DiffSummary(
                        totalFilesChanged = 7,
                        totalAdditions = 164,
                        totalDeletions = 14
                    )

                    DiffSummaryCard(
                        diffSummary = summary,
                        onInspectDiff = { onNavigateToDiff(task.id) },
                        onAcceptAll = {
                            viewModel.approveSquashMerge(task.id) {
                                // Task merged
                            }
                        },
                        onRejectAll = { viewModel.rejectTask(task.id) }
                    )
                }

                // Merged Status Banner
                if (task.state == TaskState.MERGED) {
                    item {
                        Surface(
                            shape = RoundedCornerShape(10.dp),
                            color = PassGreen.copy(alpha = 0.15f),
                            modifier = Modifier
                                .fillMaxWidth()
                                .border(1.dp, PassGreen.copy(alpha = 0.4f), RoundedCornerShape(10.dp))
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.CheckCircle,
                                    contentDescription = null,
                                    tint = PassGreen,
                                    modifier = Modifier.size(18.dp)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = "All changes squash-merged into main repository!",
                                    color = PassGreen,
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.SemiBold
                                )
                            }
                        }
                    }
                }
            }

            // Fallback when no active task yet
            if (activeTask == null) {
                item {
                    val previewSummary = ai.continuum.android.data.models.DiffSummary(
                        totalFilesChanged = 7,
                        totalAdditions = 164,
                        totalDeletions = 14,
                        files = listOf(
                            ai.continuum.android.data.models.FileDiff("mobile/.../ChatScreen.kt", additions = 2, deletions = 2),
                            ai.continuum.android.data.models.FileDiff("mobile/.../DiffViewerScreen.kt", additions = 4, deletions = 4),
                            ai.continuum.android.data.models.FileDiff("mobile/.../SettingsScreen.kt", additions = 2, deletions = 2),
                            ai.continuum.android.data.models.FileDiff("vibe_server/main.py", additions = 49, deletions = 6),
                            ai.continuum.android.data.models.FileDiff("tests/test_e2e_workflow.py", additions = 76, deletions = 0),
                            ai.continuum.android.data.models.FileDiff("vibe_server/core/config.py", additions = 3, deletions = 6),
                            ai.continuum.android.data.models.FileDiff(".gitignore", additions = 29, deletions = 0)
                        )
                    )

                    DiffSummaryCard(
                        diffSummary = previewSummary,
                        onInspectDiff = { },
                        onAcceptAll = { },
                        onRejectAll = { }
                    )
                }
            }

            // Loading state indicator
            if (uiState is ChatUiState.Loading) {
                item {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator(color = SecondaryBlue, modifier = Modifier.size(24.dp))
                    }
                }
            }
        }
    }
}
