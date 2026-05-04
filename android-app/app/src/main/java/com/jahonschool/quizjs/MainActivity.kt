package com.jahonschool.quizjs

import android.annotation.SuppressLint
import android.app.DownloadManager
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.webkit.CookieManager
import android.webkit.DownloadListener
import android.webkit.URLUtil
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import com.jahonschool.quizjs.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private var fileChooserCallback: ValueCallback<Array<Uri>>? = null

    private val filePickerLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            val uris = WebChromeClient.FileChooserParams.parseResult(result.resultCode, result.data)
            fileChooserCallback?.onReceiveValue(uris)
            fileChooserCallback = null
        }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        configureWebView()
        configureRetryActions()
        configureBackHandling()

        if (savedInstanceState == null) {
            loadHomePage()
        } else {
            binding.webView.restoreState(savedInstanceState)
        }
    }

    private fun configureRetryActions() {
        binding.swipeRefresh.setOnRefreshListener {
            binding.webView.reload()
        }

        binding.retryButton.setOnClickListener {
            loadHomePage()
        }
    }

    private fun configureBackHandling() {
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (binding.webView.canGoBack()) {
                    binding.webView.goBack()
                } else {
                    finish()
                }
            }
        })
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun configureWebView() = with(binding.webView) {
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.databaseEnabled = true
        settings.loadsImagesAutomatically = true
        settings.mixedContentMode = WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE
        settings.cacheMode = WebSettings.LOAD_DEFAULT
        settings.mediaPlaybackRequiresUserGesture = false
        settings.allowFileAccess = true
        settings.allowContentAccess = true
        settings.builtInZoomControls = false
        settings.displayZoomControls = false
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true

        CookieManager.getInstance().setAcceptCookie(true)
        CookieManager.getInstance().setAcceptThirdPartyCookies(this, true)

        webViewClient = QuizWebViewClient()
        webChromeClient = QuizWebChromeClient()

        setDownloadListener(buildDownloadListener())
    }

    private fun buildDownloadListener(): DownloadListener {
        return DownloadListener { url, userAgent, contentDisposition, mimeType, _ ->
            try {
                val request = DownloadManager.Request(Uri.parse(url)).apply {
                    setMimeType(mimeType)
                    addRequestHeader("User-Agent", userAgent)
                    setDescription(getString(R.string.download_started))
                    setTitle(URLUtil.guessFileName(url, contentDisposition, mimeType))
                    allowScanningByMediaScanner()
                    setNotificationVisibility(
                        DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED
                    )
                    setDestinationInExternalPublicDir(
                        Environment.DIRECTORY_DOWNLOADS,
                        URLUtil.guessFileName(url, contentDisposition, mimeType)
                    )
                }

                val downloadManager = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
                downloadManager.enqueue(request)
                Toast.makeText(this, R.string.download_started, Toast.LENGTH_SHORT).show()
            } catch (_: Exception) {
                Toast.makeText(this, R.string.download_failed, Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun loadHomePage() {
        showWebView()
        binding.webView.loadUrl(getString(R.string.base_url))
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        binding.webView.saveState(outState)
    }

    override fun onDestroy() {
        fileChooserCallback?.onReceiveValue(null)
        fileChooserCallback = null
        binding.webView.destroy()
        super.onDestroy()
    }

    private fun showWebView() {
        binding.errorGroup.alpha = 0f
        binding.errorGroup.animate().alpha(0f).setDuration(120).withEndAction {
            binding.errorGroup.visibility = android.view.View.GONE
            binding.swipeRefresh.visibility = android.view.View.VISIBLE
        }.start()
    }

    private fun showError() {
        binding.swipeRefresh.isRefreshing = false
        binding.swipeRefresh.visibility = android.view.View.GONE
        binding.errorGroup.alpha = 0f
        binding.errorGroup.visibility = android.view.View.VISIBLE
        binding.errorGroup.animate().alpha(1f).setDuration(180).start()
    }

    private inner class QuizWebViewClient : WebViewClient() {
        override fun shouldOverrideUrlLoading(
            view: WebView?,
            request: WebResourceRequest?
        ): Boolean {
            val uri = request?.url ?: return false
            val scheme = uri.scheme.orEmpty()
            val host = uri.host.orEmpty()
            val appHost = Uri.parse(getString(R.string.base_url)).host.orEmpty()

            return when {
                scheme == "http" || scheme == "https" -> {
                    if (host == appHost) {
                        false
                    } else {
                        startActivity(Intent(Intent.ACTION_VIEW, uri))
                        true
                    }
                }

                scheme == "tel" || scheme == "mailto" || scheme == "geo" -> {
                    startActivity(Intent(Intent.ACTION_VIEW, uri))
                    true
                }

                else -> {
                    try {
                        startActivity(Intent(Intent.ACTION_VIEW, uri))
                    } catch (_: ActivityNotFoundException) {
                        Toast.makeText(
                            this@MainActivity,
                            R.string.unsupported_link,
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                    true
                }
            }
        }

        override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
            binding.progressBar.show()
            binding.swipeRefresh.isRefreshing = true
            super.onPageStarted(view, url, favicon)
        }

        override fun onPageFinished(view: WebView?, url: String?) {
            binding.progressBar.hide()
            binding.swipeRefresh.isRefreshing = false
            showWebView()
            super.onPageFinished(view, url)
        }

        override fun onReceivedError(
            view: WebView?,
            request: WebResourceRequest?,
            error: WebResourceError?
        ) {
            if (request?.isForMainFrame == true) {
                binding.progressBar.hide()
                showError()
            }
            super.onReceivedError(view, request, error)
        }
    }

    private inner class QuizWebChromeClient : WebChromeClient() {
        override fun onShowFileChooser(
            webView: WebView?,
            filePathCallback: ValueCallback<Array<Uri>>?,
            fileChooserParams: FileChooserParams?
        ): Boolean {
            fileChooserCallback?.onReceiveValue(null)
            fileChooserCallback = filePathCallback

            return try {
                val intent = fileChooserParams?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT)
                filePickerLauncher.launch(intent)
                true
            } catch (_: ActivityNotFoundException) {
                fileChooserCallback = null
                Toast.makeText(this@MainActivity, R.string.file_picker_missing, Toast.LENGTH_SHORT)
                    .show()
                false
            }
        }
    }
}
