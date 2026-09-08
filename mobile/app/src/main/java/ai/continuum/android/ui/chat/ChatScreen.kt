package ai.continuum.android.ui.chat

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import ai.continuum.android.data.models.ProjectInfo
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
    val projects by viewModel.projects.collectAsState()
    val activeProject by viewModel.activeProject.collectAsState()
    val messages by viewModel.messages.collectAsState()
    var showProjectPicker by remember { mutableStateOf(false) }
    val listState = androidx.compose.foundation.lazy.rememberLazyListState()

    LaunchedEffect(messages.size, uiState) {
        if (messages.isNotEmpty() || uiState is ChatUiState.Loading) {
            val target = if (uiState is ChatUiState.Loading) messages.size else maxOf(0, messages.size - 1)
            listState.animateScrollToItem(target)
        }
    }

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
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(
                                    text = "Agent",
                                    fontSize = 11.sp,
                                    color = TextSecondary,
                                    fontWeight = FontWeight.Medium
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Surface(
                                    shape = RoundedCornerShape(4.dp),
                                    color = PrimaryCyan.copy(alpha = 0.15f),
                                    border = androidx.compose.foundation.BorderStroke(0.5.dp, PrimaryCyan.copy(alpha = 0.5f))
                                ) {
                                    Text(
                                        text = "⚡ Gemini 3.8 Flash",
                                        fontSize = 9.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = PrimaryCyan,
                                        modifier = Modifier.padding(horizontal = 5.dp, vertical = 1.dp)
                                    )
                                }
                            }
                            Spacer(modifier = Modifier.height(2.dp))

                            // Interactive Project Selector Pill
                            Surface(
                                shape = RoundedCornerShape(8.dp),
                                color = SurfaceCard,
                                modifier = Modifier
                                    .clip(RoundedCornerShape(8.dp))
                                    .clickable { showProjectPicker = true }
                                    .border(0.5.dp, CardBorder, RoundedCornerShape(8.dp))
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                ) {
                                    Text(text = "📁", fontSize = 12.sp)
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text(
                                        text = activeProject?.name ?: "Select Project",
                                        color = TextPrimary,
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.SemiBold
                                    )
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text(
                                        text = "(${activeProject?.currentBranch ?: "main"})",
                                        color = PrimaryCyan,
                                        fontSize = 11.sp,
                                        fontFamily = FontFamily.Monospace
                                    )
                                    Spacer(modifier = Modifier.width(2.dp))
                                    Icon(
                                        imageVector = Icons.Default.KeyboardArrowDown,
                                        contentDescription = "Select Project",
                                        tint = TextSecondary,
                                        modifier = Modifier.size(14.dp)
                                    )
                                }
                            }
                        }

                        // Action Icons: Clear Chat, Refresh, Settings
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            IconButton(onClick = { viewModel.clearChatSession() }) {
                                Icon(
                                    imageVector = Icons.Default.DeleteOutline,
                                    contentDescription = "Clear Chat Session",
                                    tint = TextSecondary,
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                            IconButton(onClick = { viewModel.loadProjects() }) {
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
                        .padding(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    // Modern Streamlined AI Chat Input Capsule
                    Card(
                        shape = RoundedCornerShape(24.dp),
                        colors = CardDefaults.cardColors(containerColor = SurfaceCard),
                        modifier = Modifier
                            .fillMaxWidth()
                            .border(1.dp, CardBorder, RoundedCornerShape(24.dp))
                    ) {
                        Column {
                            // Subtle progress line while waiting for AI
                            if (uiState is ChatUiState.Loading) {
                                LinearProgressIndicator(
                                    color = PrimaryCyan,
                                    trackColor = CardBorder,
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(2.dp)
                                )
                            }
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                // Text Input Field
                                TextField(
                                    value = promptInput,
                                    onValueChange = { promptInput = it },
                                    placeholder = {
                                        Text(
                                            "Ask anything for ${activeProject?.name ?: "workspace"}...",
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
                                        .weight(1f)
                                        .heightIn(min = 40.dp, max = 120.dp)
                                )

                                Spacer(modifier = Modifier.width(4.dp))

                                // Inline Send Button (Aligned to the right of input field)
                                IconButton(
                                    onClick = {
                                        if (promptInput.isNotBlank() && uiState !is ChatUiState.Loading) {
                                            val textToSend = promptInput
                                            promptInput = ""
                                            viewModel.sendPrompt(textToSend)
                                        }
                                    },
                                    enabled = promptInput.isNotBlank() && uiState !is ChatUiState.Loading,
                                    colors = IconButtonDefaults.iconButtonColors(
                                        containerColor = if (promptInput.isNotBlank()) IDEButtonBlue else IDETagBg,
                                        contentColor = TextPrimary,
                                        disabledContainerColor = IDETagBg.copy(alpha = 0.5f),
                                        disabledContentColor = TextMuted
                                    ),
                                    modifier = Modifier.size(36.dp)
                                ) {
                                    if (uiState is ChatUiState.Loading) {
                                        CircularProgressIndicator(
                                            color = PrimaryCyan,
                                            strokeWidth = 2.dp,
                                            modifier = Modifier.size(16.dp)
                                        )
                                    } else {
                                        Icon(
                                            imageVector = Icons.AutoMirrored.Filled.Send,
                                            contentDescription = "Send",
                                            modifier = Modifier.size(16.dp)
                                        )
                                    }
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
        androidx.compose.foundation.lazy.LazyColumn(
            state = listState,
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Case 1: Empty state placeholder (only shown if truly no messages yet)
            if (messages.isEmpty() && activeTask == null) {
                item {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 40.dp, horizontal = 20.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Surface(
                            shape = RoundedCornerShape(16.dp),
                            color = PrimaryCyan.copy(alpha = 0.1f),
                            border = androidx.compose.foundation.BorderStroke(1.dp, PrimaryCyan.copy(alpha = 0.3f)),
                            modifier = Modifier.size(54.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Text("💬", fontSize = 26.sp)
                            }
                        }
                        Spacer(modifier = Modifier.height(14.dp))
                        Text(
                            text = "${activeProject?.name ?: "Continuum"} AI Pair Programmer",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold,
                            color = TextPrimary
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = "프로젝트에 대한 질문, 코드 작성 및 리팩토링 작업을 대화로 요청하세요.",
                            fontSize = 12.sp,
                            color = TextSecondary,
                            textAlign = androidx.compose.ui.text.style.TextAlign.Center
                        )
                    }
                }
            }

            // Case 2: Render message conversation stream
            messages.forEach { msg ->
                if (msg.isUser) {
                    // User Message Bubble (Right Aligned, Clean Modern Messenger Style)
                    item(key = msg.id) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.End
                        ) {
                            Surface(
                                shape = RoundedCornerShape(16.dp, 4.dp, 16.dp, 16.dp),
                                color = IDEButtonBlue.copy(alpha = 0.22f),
                                modifier = Modifier
                                    .widthIn(max = 300.dp)
                                    .border(1.dp, IDEButtonBlue.copy(alpha = 0.5f), RoundedCornerShape(16.dp, 4.dp, 16.dp, 16.dp))
                            ) {
                                androidx.compose.foundation.layout.Box(modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp)) {
                                    Text(
                                        text = msg.text,
                                        color = TextPrimary,
                                        fontSize = 14.sp,
                                        lineHeight = 20.sp
                                    )
                                }
                            }
                        }
                    }
                } else if (msg.isError) {
                    // Error Card
                    item(key = msg.id) {
                        Surface(
                            shape = RoundedCornerShape(10.dp),
                            color = MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.2f),
                            modifier = Modifier
                                .fillMaxWidth()
                                .border(1.dp, MaterialTheme.colorScheme.error.copy(alpha = 0.5f), RoundedCornerShape(10.dp))
                        ) {
                            Row(modifier = Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Default.Warning, contentDescription = null, tint = MaterialTheme.colorScheme.error, modifier = Modifier.size(18.dp))
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(text = msg.text, color = TextPrimary, fontSize = 13.sp)
                            }
                        }
                    }
                } else if (msg.task != null) {
                    val task = msg.task

                    // Assistant explanation bubble if text is present
                    if (msg.text.isNotBlank()) {
                        item(key = "${msg.id}_reply") {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.Start
                            ) {
                                Surface(
                                    shape = RoundedCornerShape(4.dp, 16.dp, 16.dp, 16.dp),
                                    color = SurfaceCard,
                                    modifier = Modifier
                                        .widthIn(max = 340.dp)
                                        .border(1.dp, CardBorder, RoundedCornerShape(4.dp, 16.dp, 16.dp, 16.dp))
                                ) {
                                    Column(modifier = Modifier.padding(14.dp)) {
                                        AiSenderBadge(engine = msg.engine)
                                        Spacer(modifier = Modifier.height(6.dp))
                                        Text(text = msg.text, color = TextPrimary, fontSize = 14.sp, lineHeight = 20.sp)
                                    }
                                }
                            }
                        }
                    }



                    // Lens evaluation card (if available)
                    task.lensReport?.let { report ->
                        item(key = "${msg.id}_lens") {
                            LensEvaluationCard(
                                report = report,
                                onApprove = { viewModel.approveDesign(task.id) },
                                onReject = { viewModel.rejectTask(task.id) },
                                isActionable = task.state == TaskState.AWAITING_DESIGN_APPROVAL
                            )
                        }
                    }

                    // Diff summary card (REAL diffs only - Zero Fake)
                    task.diffSummary?.let { diff ->
                        item(key = "${msg.id}_diff") {
                            DiffSummaryCard(
                                diffSummary = diff,
                                onInspectDiff = { onNavigateToDiff(task.id) },
                                onAcceptAll = {
                                    viewModel.approveSquashMerge(task.id) { }
                                },
                                onRejectAll = { viewModel.rejectTask(task.id) },
                                verificationReport = task.verificationReport,
                                lensReport = task.lensReport,
                                isActionable = task.state == TaskState.AWAITING_MERGE_APPROVAL
                            )
                        }
                    }

                    // Merged Status Banner
                    if (task.state == TaskState.MERGED) {
                        item(key = "${msg.id}_merged") {
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
                } else {
                    // Standard AI Assistant Chat Bubble (Direct Conversation / Notice)
                    item(key = msg.id) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.Start
                        ) {
                            Surface(
                                shape = RoundedCornerShape(4.dp, 16.dp, 16.dp, 16.dp),
                                color = SurfaceCard,
                                modifier = Modifier
                                    .widthIn(max = 340.dp)
                                    .border(1.dp, CardBorder, RoundedCornerShape(4.dp, 16.dp, 16.dp, 16.dp))
                            ) {
                                Column(modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp)) {
                                    AiSenderBadge(engine = msg.engine)
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Text(
                                        text = msg.text,
                                        color = TextPrimary,
                                        fontSize = 14.sp,
                                        lineHeight = 20.sp
                                    )
                                }
                            }
                        }
                    }
                }
            }

            // Natural AI Typing / Thinking Bubble (No fake diagnostics or premature analysis claims)
            if (uiState is ChatUiState.Loading) {
                item(key = "typing_bubble") {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.Start
                    ) {
                        Surface(
                            shape = RoundedCornerShape(4.dp, 16.dp, 16.dp, 16.dp),
                            color = SurfaceCard,
                            modifier = Modifier.border(0.5.dp, CardBorder, RoundedCornerShape(4.dp, 16.dp, 16.dp, 16.dp))
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp)
                            ) {
                                Text(text = "🤖", fontSize = 14.sp)
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = "Continuum이 답변을 작성하고 있습니다...",
                                    fontSize = 13.sp,
                                    color = TextSecondary
                                )
                            }
                        }
                    }
                }
            }
        }
    }

    // Modal Bottom Sheet: Project Picker
    if (showProjectPicker) {
        ModalBottomSheet(
            onDismissRequest = { showProjectPicker = false },
            containerColor = SurfaceDark
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp, vertical = 12.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = "📂 프로젝트 열기 (Open Project)",
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary
                    )
                    IconButton(onClick = { viewModel.loadProjects() }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh", tint = PrimaryCyan, modifier = Modifier.size(20.dp))
                    }
                }

                Text(
                    text = "맥북 워크스페이스 내 Git 저장소를 선택하세요.",
                    fontSize = 12.sp,
                    color = TextSecondary,
                    modifier = Modifier.padding(bottom = 12.dp)
                )

                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxWidth().heightIn(max = 360.dp)
                ) {
                    items(projects) { proj ->
                        val isSelected = activeProject?.path == proj.path
                        Surface(
                            shape = RoundedCornerShape(10.dp),
                            color = if (isSelected) SurfaceCard else BackgroundDark,
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    viewModel.selectProject(proj)
                                    showProjectPicker = false
                                }
                                .border(
                                    width = if (isSelected) 1.5.dp else 0.5.dp,
                                    color = if (isSelected) PrimaryCyan else CardBorder,
                                    shape = RoundedCornerShape(10.dp)
                                )
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.SpaceBetween,
                                modifier = Modifier.padding(12.dp)
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                                    val emoji = when (proj.name) {
                                        "deartalk-ai" -> "📱"
                                        "skybrain" -> "🧠"
                                        "continuum" -> "🌌"
                                        "skynexus" -> "☁️"
                                        "myskynet" -> "🌐"
                                        else -> "📁"
                                    }
                                    Text(text = emoji, fontSize = 20.sp)
                                    Spacer(modifier = Modifier.width(12.dp))
                                    Column {
                                        Text(
                                            text = proj.name,
                                            fontWeight = FontWeight.SemiBold,
                                            fontSize = 14.sp,
                                            color = TextPrimary
                                        )
                                        Text(
                                            text = proj.path.substringAfterLast("OSSProject/"),
                                            fontSize = 11.sp,
                                            color = TextSecondary,
                                            maxLines = 1,
                                            overflow = TextOverflow.Ellipsis
                                        )
                                    }
                                }

                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Surface(
                                        shape = RoundedCornerShape(4.dp),
                                        color = IDETagBg,
                                        modifier = Modifier.padding(end = 8.dp)
                                    ) {
                                        Text(
                                            text = proj.currentBranch,
                                            color = PrimaryCyan,
                                            fontSize = 11.sp,
                                            fontFamily = FontFamily.Monospace,
                                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                        )
                                    }
                                    if (isSelected) {
                                        Icon(
                                            imageVector = Icons.Default.CheckCircle,
                                            contentDescription = "Selected",
                                            tint = PassGreen,
                                            modifier = Modifier.size(18.dp)
                                        )
                                    }
                                }
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))
            }
        }
    }
}

@Composable
fun AiSenderBadge(engine: String?) {
    val cleanEngine = engine?.lowercase() ?: ""
    val (badgeText, badgeColor) = when {
        cleanEngine.contains("antigravity") || cleanEngine.contains("agy") -> "✨ Antigravity (Gemini 3.8)" to PrimaryCyan
        cleanEngine.contains("skybrain") -> "⚡ Local SkyBrain (Qwen 3.8)" to AccentPurple
        cleanEngine.contains("gemini-3.8") || cleanEngine.contains("3.8") -> "🤖 Cloud Gemini (3.8 Flash)" to PrimaryCyan
        cleanEngine.contains("gemini") -> "🤖 Cloud Gemini" to PrimaryCyan
        engine.isNullOrBlank() -> "🤖 Continuum AI" to TextSecondary
        else -> "🤖 $engine" to PrimaryCyan
    }

    Surface(
        shape = RoundedCornerShape(4.dp),
        color = IDEPillBg,
        modifier = Modifier.padding(bottom = 4.dp)
    ) {
        Text(
            text = badgeText,
            color = badgeColor,
            fontSize = 11.sp,
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
        )
    }
}
