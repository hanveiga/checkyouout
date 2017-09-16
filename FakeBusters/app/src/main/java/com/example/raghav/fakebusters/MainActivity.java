package com.example.raghav.fakebusters;

import android.content.Context;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.JsonHttpResponseHandler;
import com.loopj.android.http.RequestParams;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;

import cz.msebera.android.httpclient.Header;

public class MainActivity extends AppCompatActivity {

    String debugTag = "WebView";
    WebView myWebView;
    AsyncHttpClient client;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        myWebView = (WebView) findViewById(R.id.webview);
        myWebView.setWebViewClient(new myWebClient());
        //myWebView.loadUrl("https://news.google.com/");
        myWebView.loadUrl("http://terrillthompson.com/tests/youtube.html");
        WebSettings webSettings = myWebView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setAllowUniversalAccessFromFileURLs(true);
        webSettings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        myWebView.addJavascriptInterface(new JavaScriptInterface(this), "Android");

        client = new AsyncHttpClient();
        client.setResponseTimeout(20 * 10000);
    }

    class myWebClient extends WebViewClient {

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            return false;
        }

        @Override
        public void onPageFinished(WebView view, String url) {
            // TODO Auto-generated method stub
            super.onPageFinished(view, url);
            Log.i(debugTag, "Page Loading completed");

            //checkYouTubeTranscript("bRaWY4cZB1c");

            injectScriptFile(myWebView, "js/jquery-3.2.1.min.js");
            injectScriptFile(myWebView, "js/jquery.mobile-1.4.5.min.js");
            injectScriptFile(myWebView, "js/youtube_iframe_api.js");
            //injectScriptFile(myWebView, "js/checkYoutubeTranscript.js");

            getYoutubeVideoId();


            String jsCode = "javascript:$('a').each( function () { $(this).css('background-color', 'yellow') } ); undefined";
            myWebView.loadUrl(jsCode);
        }

        private void getYoutubeVideoId(){
            injectScriptFile(myWebView, "js/getYoutubeVideoId.js");
        }



        private void injectScriptFile(WebView view, String scriptFile) {
            InputStream input;
            try {
                input = getAssets().open(scriptFile);
                byte[] buffer = new byte[input.available()];
                input.read(buffer);
                input.close();

                // String-ify the script byte-array using BASE64 encoding !!!
                String encoded = Base64.encodeToString(buffer, Base64.NO_WRAP);
                view.loadUrl("javascript:(function() {" +
                        "var parent = document.getElementsByTagName('head').item(0);" +
                        "var script = document.createElement('script');" +
                        "script.type = 'text/javascript';" +
                        // Tell the browser to BASE64-decode the string into your script !!!
                        "script.innerHTML = window.atob('" + encoded + "');" +
                        "parent.appendChild(script)" +
                        "})()");
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        }
    }

    public class JavaScriptInterface {
        Context mContext;

        /** Instantiate the interface and set the context */
        JavaScriptInterface(Context c) {
            mContext = c;
        }

        @JavascriptInterface
        public void videoCallback(String id) {
            Log.d("myWebView" , "Id of the video found = "+ id);
            checkYouTubeTranscript(id);
        }

        private void  checkYouTubeTranscript(String id) {
            RequestParams rp = new RequestParams();
            rp.add("id", id);

            client.get("http://172.30.3.43:8001/videototext", rp, new JsonHttpResponseHandler() {
                @Override
                public void onSuccess(int statusCode, Header[] headers, JSONObject response) {
                    // If the response is JSONObject instead of expected JSONArray
                    Log.d("asd", "---------------- this is response : " + response);
                    try {
                        JSONObject serverResp = new JSONObject(response.toString());
                    } catch (JSONException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }

                @Override
                public void onFailure(int statusCode, Header[] headers, Throwable throwable, JSONObject object){
                    // Pull out the first event on the public timeline
                    Log.d("asd", "error : " + throwable.getMessage());
                }
            });
        }
    }
}
