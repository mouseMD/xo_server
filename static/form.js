function openLoginForm() {
  document.getElementById("loginForm").style.display = "block";
    document.getElementById("register-button").disabled = true;
  document.getElementById("login-button").disabled = true;
}

function closeLoginForm() {

  document.getElementById("loginForm").style.display = "none";
    document.getElementById("register-button").disabled = false;
    document.getElementById("login-button").disabled = false;
}

function openRegisterForm() {
  document.getElementById("registerForm").style.display = "block";
  document.getElementById("register-button").disabled = true;
  document.getElementById("login-button").disabled = true;
}

function closeRegisterForm() {
  document.getElementById("registerForm").style.display = "none";
  document.getElementById("register-button").disabled = false;
    document.getElementById("login-button").disabled = false;
}