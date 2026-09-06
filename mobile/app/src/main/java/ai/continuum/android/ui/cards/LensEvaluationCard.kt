package ai.continuum.android.ui.cards

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.continuum.android.data.models.LensReport
import ai.continuum.android.ui.theme.*

@Composable
fun LensEvaluationCard(
    report: LensReport,
    onApprove: () -> Unit,
    onReject: () -> Unit,
    isActionable: Boolean = true,
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }

    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
        modifier = modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Header: Title & Overall Score Badge
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = if (report.overallPassed) Icons.Default.CheckCircle else Icons.Default.Warning,
                        contentDescription = null,
                        tint = if (report.overallPassed) PassGreen else WarningYellow,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "SkyBrain 5-Lens Review",
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp,
                        color = TextPrimary
                    )
                }

                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(if (report.overallPassed) PassGreen.copy(alpha = 0.2f) else FailRed.copy(alpha = 0.2f))
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "${report.averageScore.toInt()} / 100",
                        fontWeight = FontWeight.Bold,
                        color = if (report.overallPassed) PassGreen else FailRed,
                        fontSize = 13.sp
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // 5 Lenses Horizontal Badges Grid
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                report.evaluations.forEach { (key, eval) ->
                    LensBadge(
                        name = when (key) {
                            "clean_code" -> "CleanCode"
                            "clean_architecture" -> "Arch"
                            "security" -> "Security"
                            "performance" -> "Perf"
                            "ai_conduct" -> "AIConduct"
                            else -> key.take(5)
                        },
                        passed = eval.passed,
                        score = eval.score
                    )
                }
            }

            Spacer(modifier = Modifier.height(10.dp))
            Text(
                text = report.summary,
                color = TextSecondary,
                fontSize = 13.sp
            )

            // Details Toggle
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier
                    .clickable { expanded = !expanded }
                    .padding(vertical = 8.dp)
            ) {
                Text(
                    text = if (expanded) "Hide Detailed Findings" else "View Lens Findings",
                    color = PrimaryCyan,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold
                )
                Icon(
                    imageVector = if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    contentDescription = null,
                    tint = PrimaryCyan,
                    modifier = Modifier.size(18.dp)
                )
            }

            AnimatedVisibility(visible = expanded) {
                Column(modifier = Modifier.padding(top = 4.dp)) {
                    report.evaluations.values.forEach { eval ->
                        if (eval.findings.isNotEmpty()) {
                            Text(
                                text = "• ${eval.lensName}:",
                                fontWeight = FontWeight.SemiBold,
                                color = TextPrimary,
                                fontSize = 13.sp
                            )
                            eval.findings.forEach { finding ->
                                Text(
                                    text = "  - [${finding.severity}] ${finding.description}",
                                    color = if (finding.severity == "CRITICAL" || finding.severity == "HIGH") FailRed else TextMuted,
                                    fontSize = 12.sp,
                                    modifier = Modifier.padding(start = 8.dp, bottom = 2.dp)
                                )
                            }
                        }
                    }
                }
            }

            // Action Buttons
            if (isActionable) {
                Spacer(modifier = Modifier.height(12.dp))
                Row(modifier = Modifier.fillMaxWidth()) {
                    OutlinedButton(
                        onClick = onReject,
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = FailRed),
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(Icons.Default.Close, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Reject")
                    }

                    Spacer(modifier = Modifier.width(8.dp))

                    Button(
                        onClick = onApprove,
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryCyan),
                        modifier = Modifier.weight(2f)
                    ) {
                        Text("Approve & Sandbox Run", color = BackgroundDark, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@Composable
fun LensBadge(name: String, passed: Boolean, score: Int) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .clip(RoundedCornerShape(6.dp))
            .background(SurfaceCard)
            .padding(horizontal = 6.dp, vertical = 4.dp)
    ) {
        Text(text = name, fontSize = 10.sp, color = TextSecondary)
        Text(
            text = "$score",
            fontWeight = FontWeight.Bold,
            fontSize = 12.sp,
            color = if (passed) PassGreen else FailRed
        )
    }
}
