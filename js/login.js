$('#loginform').submit(e => {
    e.preventDefault();
    const email = $('#email').val()
    const password = $('#psw').val()
    login(email, password)
})

async function login(email, password){
    const form = new FormData()
    form.append("email", email)
    form.append("password", password)
    setLoading()
    const response = await fetch(`${apiUrl}/sign-in/`, {
        method: "POST",
        body: form
    }).then(r => r.json())
    unsetLoading()

    if (response.status){
        loginSuccess()
    }else{
        loginFailed(response.error)
    }
}

function loginSuccess(){
    console.log("logged in")
    window.location.replace(dashboardUrl)
}

function loginFailed(message){
    showToast("Login failed", message)
}