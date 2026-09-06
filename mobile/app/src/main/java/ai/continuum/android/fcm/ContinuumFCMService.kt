package ai.continuum.android.fcm

import android.app.PendingIntent
import android.content.Intent
import android.net.Uri
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import ai.continuum.android.ContinuumApp
import ai.continuum.android.MainActivity
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

class ContinuumFCMService : FirebaseMessagingService() {

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        // In real deployment: send token to Vibe Server
    }

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)

        val data = remoteMessage.data
        val taskId = data["task_id"] ?: return
        val title = data["title"] ?: remoteMessage.notification?.title ?: "Continuum Notification"
        val body = data["body"] ?: remoteMessage.notification?.body ?: "Task update ready"
        val actionType = data["action_type"]

        showNotification(taskId, title, body, actionType)
    }

    private fun showNotification(taskId: String, title: String, body: String, actionType: String?) {
        val deepLinkUri = when (actionType) {
            "MERGE_APPROVAL" -> Uri.parse("continuum://tasks/$taskId/diff")
            else -> Uri.parse("continuum://tasks/$taskId")
        }

        val intent = Intent(Intent.ACTION_VIEW, deepLinkUri, this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }

        val pendingIntent = PendingIntent.getActivity(
            this,
            taskId.hashCode(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(this, ContinuumApp.CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .build()

        try {
            NotificationManagerCompat.from(this).notify(taskId.hashCode(), notification)
        } catch (_: SecurityException) {
            // Permission not granted yet
        }
    }
}
