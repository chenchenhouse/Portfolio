function show_hide() {
    var login = document.getElementById("container1");
    var signup = document.getElementById("container2");
    var copyright = document.getElementById("copyright");
  
    if (signup.style.display === "block") {
        login.style.display = "block";  //login出現
        document.getElementById("username").value="";
        document.getElementById("password").value="";
        login.style.visibility="visible";
        signup.style.display = "none";  //signup消失
        copyright.style.margin = "10px 0px 0px 0px";
    } else {
        login.style.display = "none";   //login消失
        signup.style.display = "block"; //signup出現
        copyright.style.margin = "10px 0px 0px 0px";
     
        document.getElementById("username2").value="";
        document.getElementById("password2").value="";
        document.getElementById("comfirm_password").value="";
    }
}

function check(){
    var p1 = document.getElementById("password2").value;
    var p2 = document.getElementById("comfirm_password").value;
    var u2 = document.getElementById("username2").value;
    if(u2.length < 3){
        document.getElementById("tishi").innerHTML="<font class='check' color='red'>帳號不得小於3碼</font>";
        document.getElementById("submit").disabled = true; 
    }
    else if(p1 == '' && p2 == ''){
        document.getElementById("tishi").innerHTML="<font class='check' color='red'>密碼不得為空</font>";
        document.getElementById("submit").disabled = true; 
    }
    else if(p1.length < 6){
        document.getElementById("tishi").innerHTML="<font class='check' color='red'>密碼不得小於6碼</font>";
        document.getElementById("submit").disabled = true;
    }
    else if(p2 == ''){
        document.getElementById("tishi").innerHTML="<font class='check' color='red'>確認密碼不得為空</font>";
        document.getElementById("submit").disabled = true;
    }
    else if(p1 == ''){
        document.getElementById("tishi").innerHTML="<font class='check' color='red'>密碼不得為空</font>";
        document.getElementById("submit").disabled = true;
    }
    else if ( p1 == p2 ) {
        document.getElementById("tishi").innerHTML="<font class='check' color='green'>確認密碼相同</font>";
        document.getElementById("submit").disabled = false;
    }
    else {
        document.getElementById("tishi").innerHTML="<font class='check' color='red'>確認密碼不相同</font>";
        document.getElementById("submit").disabled = true;
    }
}

function password_hide(){
    var password = document.getElementById('password');
    var anniu = document.getElementById('password_conceal');
    if(password.type==='password')
    {
        password.setAttribute('type','text');
        anniu.classList.add('yincang');
    }else{
    password.setAttribute('type','password');
        anniu.classList.remove('yincang');
    }
}


function password2_hide(){
    var password = document.getElementById('password2');
    var anniu = document.getElementById('conceal');
    if(password.type==='password')
    {
        password.setAttribute('type','text');
        anniu.classList.add('yincang');
    }else{
    password.setAttribute('type','password');
        anniu.classList.remove('yincang');
    }
}

function comfirm_password_hide(){
    var password = document.getElementById('comfirm_password');
    var anniu = document.getElementById('comfirm_conceal');
    if(password.type==='password')
    {
        password.setAttribute('type','text');
        anniu.classList.add('yincang');
    }else{
    password.setAttribute('type','password');
        anniu.classList.remove('yincang');
    }
}

window.alert = function(msg, callback) {
    var div = document.createElement("div");
    div.innerHTML = "<style type=\"text/css\">"
        + ".nbaMask { position: fixed; z-index: 1000; top: 0; right: 0; left: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); }                                                                                                                                                                       "
        + ".nbaMaskTransparent { position: fixed; z-index: 1000; top: 0; right: 0; left: 0; bottom: 0; }                                                                                                                                                                                            "
        + ".nbaDialog { position: fixed; z-index: 5000; width: 80%; max-width: 300px; top: 50%; left: 50%; -webkit-transform: translate(-50%, -50%); transform: translate(-50%, -50%); background-color: #fff; text-align: center; border-radius: 8px; overflow: hidden; opacity: 1; color: white; }"
        + ".nbaDialog .nbaDialogHd { padding: .2rem .27rem .08rem .27rem; }                                                                                                                                                                                                                         "
        + ".nbaDialog .nbaDialogHd .nbaDialogTitle { font-size: 17px; font-weight: 400; }                                                                                                                                                                                                           "
        + ".nbaDialog .nbaDialogBd { padding: 0 .27rem; font-size: 15px; line-height: 1.3; word-wrap: break-word; word-break: break-all; color: #000000; }                                                                                                                                          "
        + ".nbaDialog .nbaDialogFt { position: relative; line-height: 48px; font-size: 17px; display: -webkit-box; display: -webkit-flex; display: flex; }                                                                                                                                          "
        + ".nbaDialog .nbaDialogFt:after { content: \" \"; position: absolute; left: 0; top: 0; right: 0; height: 1px; border-top: 1px solid #e6e6e6; color: #e6e6e6; -webkit-transform-origin: 0 0; transform-origin: 0 0; -webkit-transform: scaleY(0.5); transform: scaleY(0.5); }               "
        + ".nbaDialog .nbaDialogBtn { background:#e6e6e6;display: block; -webkit-box-flex: 1; -webkit-flex: 1; flex: 1; color: #000000; text-decoration: none; -webkit-tap-highlight-color: transparent; position: relative; margin-bottom: 0; }                                                                       "
        + ".nbaDialog .nbaDialogBtn:after { content: \" \"; position: absolute; left: 0; top: 0; width: 1px; bottom: 0; border-left: 1px solid #e6e6e6; color: #e6e6e6; -webkit-transform-origin: 0 0; transform-origin: 0 0; -webkit-transform: scaleX(0.5); transform: scaleX(0.5); }             "
        + ".nbaDialog a { text-decoration: none; -webkit-tap-highlight-color: transparent; }"
        + "</style>"
        + "<div id=\"dialogs2\" style=\"display: none\">"
        + "<div class=\"nbaMask\"></div>"
        + "<div class=\"nbaDialog\">"
        + " <div class=\"nbaDialogHd\">"
        + "   <strong class=\"nbaDialogTitle\"></strong>"
        + " </div>"
        + " <div class=\"nbaDialogBd\" id=\"dialog_msg2\">彈窗內容，告知當前狀態、信息和解決方法，描述文字盡量控制在三行內</div>"
        + " <div class=\"nbaDialogHd\">"
        + "   <strong class=\"nbaDialogTitle\"></strong>"
        + " </div>"
        + " <div class=\"nbaDialogFt\">"
        + "   <a href=\"javascript:;\" class=\"nbaDialogBtn nbaDialogBtnPrimary\" id=\"dialog_ok2\">確定</a>"
        + " </div></div></div>";
    document.body.appendChild(div);
   
    var dialogs2 = document.getElementById("dialogs2");
    dialogs2.style.display = 'block';
   
    var dialog_msg2 = document.getElementById("dialog_msg2");
    dialog_msg2.innerHTML = msg;
   
    // var dialog_cancel = document.getElementById("dialog_cancel");
    // dialog_cancel.onclick = function() {
    // dialogs2.style.display = 'none';
    // };
    var dialog_ok2 = document.getElementById("dialog_ok2");
    dialog_ok2.onclick = function() {
      dialogs2.style.display = 'none';
      callback();
    };
  };
 

