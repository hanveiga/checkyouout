package com.example.raghav.fakebusters;

import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.os.Build;
import android.support.v4.view.MenuItemCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ArrayAdapter;
import android.widget.Spinner;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.JsonHttpResponseHandler;
import com.loopj.android.http.RequestParams;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;

import cz.msebera.android.httpclient.Header;
import cz.msebera.android.httpclient.entity.StringEntity;

public class MainActivity extends AppCompatActivity {

    String debugTag = "WebView";
    String pythonScrapperBaseURL = "http://172.30.3.43:8877";
    String videoBaseURL = "http://172.30.3.43:8001";
    WebView myWebView;
    AsyncHttpClient client;
    String currentPage = "home";
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        myWebView = (WebView) findViewById(R.id.webview);
        myWebView.setWebViewClient(new myWebClient());
        //myWebView.loadUrl("https://news.google.com/");
        myWebView.loadUrl("https://news.google.com/news/?ned=us&hl=en");
        //myWebView.loadUrl("https://stark-wave-40519.herokuapp.com/");
        WebSettings webSettings = myWebView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setAllowUniversalAccessFromFileURLs(true);
        webSettings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        myWebView.addJavascriptInterface(new JavaScriptInterface(this), "Android");

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
            if (0 != (getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE))
            { WebView.setWebContentsDebuggingEnabled(true); }
        }

        client = new AsyncHttpClient();
        client.setResponseTimeout(20 * 100000);
    }

    @Override
    public void onBackPressed() {
        Log.d("CDA", "onBackPressed Called");
        myWebView.goBack();
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
            if(!url.toLowerCase().startsWith("https://news.google.com".toLowerCase())) {

                checkHTML(url);
                //checkYouTubeTranscript("bRaWY4cZB1c");

                injectScriptFile(myWebView, "js/jquery-3.2.1.min.js");
                injectScriptFile(myWebView, "js/jquery.mobile-1.4.5.min.js");
                injectScriptFile(myWebView, "js/videoHighlights.js");
                injectScriptFile(myWebView, "js/youtube_iframe_api.js");
                injectScriptFile(myWebView, "js/textHighlights.js");

                getYoutubeVideoId();
            }


            //String jsCode = "javascript:$('a').each( function () { $(this).css('background-color', 'yellow') } ); undefined";
            //myWebView.loadUrl(jsCode);
        }

        @Override
        public void onPageStarted(WebView view, String url,  Bitmap favico) {
            super.onPageStarted(view, url, favico);
            if(!url.toLowerCase().startsWith("https://news.google.com".toLowerCase())) {
                getSupportActionBar().setBackgroundDrawable(new ColorDrawable(Color.rgb(255, 80, 80)));
                currentPage = "away";
            }else{
                getSupportActionBar().setBackgroundDrawable(new ColorDrawable(Color.rgb(0, 102, 204)));
                currentPage = "home";
            }
        }

        private void getYoutubeVideoId(){
            injectScriptFile(myWebView, "js/getYoutubeVideoId.js");
        }

        private void  checkHTML(String url) {
            JSONObject jsonObj = new JSONObject();
            StringEntity entity = null;
            try {
                jsonObj.put("url", url);
                entity = new StringEntity(jsonObj.toString());
            } catch (Exception e) {
                e.printStackTrace();
            }
            String urlEndpoint = pythonScrapperBaseURL+"/urlcheck";
            client.post(getApplicationContext(), urlEndpoint, entity, "application/json", new JsonHttpResponseHandler() {
                @Override
                public void onSuccess(int statusCode, Header[] headers, JSONArray response) {
                    // If the response is JSONObject instead of expected JSONArray
                    Log.d("checkHTML_onSuccess", "---------------- this is response : " + response);
                    JSONArray serverResp = null;
                    try {
                       serverResp = new JSONArray(response.toString());
                        sendResultToHTML(serverResp);
                    } catch (JSONException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }

                }

                @Override
                public void onFailure(int statusCode, Header[] headers, Throwable throwable, JSONObject object){
                    // Pull out the first event on the public timeline
                    Log.d("checkHTML_onError", "error : " + throwable.getMessage());
                }

                private void sendResultToHTML(JSONArray result){
                    //myWebView.loadUrl("javascript:textHighlights('"+result.toString()+"')");
                    JSONArray finalArray = new JSONArray();
                    try {
                        for (int i = 0 ; i < result.length(); i++) {
                            JSONObject o1 = result.getJSONObject(i);

                            String pID  = o1.getString("p_id");
                            String label = o1.getString("label");
                            JSONArray a2  = o1.getJSONArray("results");

                            JSONObject o3 = a2.getJSONObject(0);
                            String docID = o3.getString("doc_id");
                            String doc_text = o3.getString("doc_text");
                            JSONObject send = new JSONObject();
                            send.put("pid", pID);
                            send.put("label", label);
                            send.put("did", docID);
                            send.put("docText", doc_text);
                            finalArray.put(send);
                        }
                        String str_finalArray = finalArray.toString();

                        myWebView.loadUrl("javascript:textHighlights('"+str_finalArray+"')");

                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                }
            });
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

        @JavascriptInterface
        public void debugCallback(String text) {
            Log.d("myWebView_Debug" ,  text);
        }

        @JavascriptInterface
        public void TextCallback(String id) {
            if(!currentPage.contains("home")) {
                getSupportActionBar().setBackgroundDrawable(new ColorDrawable(Color.rgb(0, 179, 0)));
            }
            else {

            }
        }

        private void  checkYouTubeTranscript(String id) {
            RequestParams rp = new RequestParams();
            rp.add("id", id);

            client.get(videoBaseURL+"/videototext", rp, new JsonHttpResponseHandler() {
                @Override
                public void onSuccess(int statusCode, Header[] headers, JSONObject response) {
                    // If the response is JSONObject instead of expected JSONArray
                    Log.d("asd", "---------------- this is response : " + response);
                    try {
                        JSONObject serverResp = new JSONObject(response.toString());

                        JSONArray finalO = serverResp.getJSONArray("final");

                        for(int i=0; i < finalO.length(); i++) {

                        }
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
