$('#register').submit(e => {
    e.preventDefault()
    const firstName = $("#firstName").val()
    const lastName = $("#lastName").val()
    const email = $('#email').val()
    const password = $('#password').val()
    const confirmPwd = $("#passwordConfirmation").val() 
    if (password != confirmPwd)
        return setInvalid($("#password"))
    
    register(firstName, lastName, email, password)
    
})

function setInvalid(input){
    input.addClass('is-invalid')
    setTimeout( () => {
        input.removeClass('is-invalid')
    }, 5000)
}

async function register(firstName, lastName, email, pwd){
    const form = new FormData()
    form.append("first_name", firstName)
    form.append("last_name", lastName)
    form.append("email", email)
    form.append("password", pwd)
    
    setLoading()

    const response = await fetch(`${apiUrl}/sign-up/`,
        {
            method: "POST",
            body: form
        }
    ).then(r => r.json())

    unsetLoading()
    if (response.status){
        registerSuccess()
    }else{
        registerFailed(response.error)
    }
}
function registerSuccess(){
    console.log("registered")
    window.location.replace(dashboardUrl)
}

function registerFailed(message){
    showToast("Registration failed", message)
}