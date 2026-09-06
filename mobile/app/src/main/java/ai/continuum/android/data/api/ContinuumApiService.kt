package ai.continuum.android.data.api

import ai.continuum.android.data.models.ApprovalRequest
import ai.continuum.android.data.models.DiffSummary
import ai.continuum.android.data.models.TaskCreateRequest
import ai.continuum.android.data.models.TaskResponse
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import java.util.concurrent.TimeUnit

interface ContinuumApiService {

    @GET("health")
    suspend fun checkHealth(): Response<Map<String, Any>>

    @GET("health/diagnostics")
    suspend fun getDiagnostics(): Response<Map<String, Any>>

    @POST("api/v1/tasks")
    suspend fun createTask(@Body request: TaskCreateRequest): Response<TaskResponse>

    @GET("api/v1/tasks/{taskId}")
    suspend fun getTask(@Path("taskId") taskId: String): Response<TaskResponse>

    @POST("api/v1/tasks/{taskId}/approve")
    suspend fun approveTask(
        @Path("taskId") taskId: String,
        @Body request: ApprovalRequest
    ): Response<TaskResponse>

    @GET("api/v1/tasks/{taskId}/diff")
    suspend fun getTaskDiff(@Path("taskId") taskId: String): Response<DiffSummary>
}

object NetworkModule {
    // Default host address for Android emulator (10.0.2.2 maps to host 127.0.0.1)
    private var baseUrl: String = "http://10.0.2.2:8080/"

    fun setBaseUrl(url: String) {
        baseUrl = if (url.endsWith("/")) url else "$url/"
        retrofitInstance = null
    }

    private var retrofitInstance: Retrofit? = null

    private fun getRetrofit(): Retrofit {
        return retrofitInstance ?: synchronized(this) {
            val logging = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }

            val client = OkHttpClient.Builder()
                .connectTimeout(15, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .addInterceptor(logging)
                .build()

            Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
                .also { retrofitInstance = it }
        }
    }

    val apiService: ContinuumApiService
        get() = getRetrofit().create(ContinuumApiService::class.java)
}
