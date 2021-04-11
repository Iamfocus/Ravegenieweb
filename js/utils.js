const spinner = `
    <div class="spinner-border text-primary" role="status">
    </div>
`
const toast = `
    <div aria-live="polite" class="toast-container" aria-atomic="true" style="position: relative; z-index: 999;">
    <div class="toast" style="position: absolute; top: 0; right: 0;">
    <div class="toast-header">
        <strong class="mr-auto">Bootstrap</strong>
        <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
        <span aria-hidden="true">&times;</span>
        </button>
    </div>
    <div class="toast-body">
        Hello, world! This is a toast message.
    </div>
    </div>
    </div>
`
$('body').prepend(toast)
$('.toast').toast({ delay: 5000 })

const apiUrl = "http://127.0.0.1:8000/accounts"
const dashboardUrl = "http://localhost:8000"

const submitBtn = $('.submitbtn')
const submitBtnText = submitBtn.text()

function resetToast(){
    setTimeout( () => {
        $('.toast-header').text("")
        $('.toast-body').text("")
    }, 5000)
}

function showToast(heading, body){
    $('.toast-header strong').text(heading)
    $('.toast-body').text(body)
    $('.toast').toast('show')

    resetToast()
}

function setLoading(){
    submitBtn.text("")
    submitBtn.append(spinner)
}

function unsetLoading(){
    submitBtn.empty()
    submitBtn.text(submitBtnText)
}