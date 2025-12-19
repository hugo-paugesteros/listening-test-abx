function shuffle(array) {
    let currentIndex = array.length;

    // While there remain elements to shuffle...
    while (currentIndex != 0) {

        // Pick a remaining element...
        let randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;

        // And swap it with the current element.
        [array[currentIndex], array[randomIndex]] = [
            array[randomIndex], array[currentIndex]];

        // Swap a and b
        if (Math.random() > 0.5) {
            [array[currentIndex].a, array[currentIndex].b] = [array[currentIndex].b, array[currentIndex].a]
        }
    }
    return array
}

const stepsContainer = document.querySelector('#steps')
const formContainer = document.querySelector('form')
const progressLine = document.querySelector('#progress')
const prevBtn = document.querySelector('#prev')
const nextBtn = document.querySelector('#next')

// State
let roundsData = []
let currentPage = window.location.hash ? parseInt(location.hash.substring(1)) : 1

// Init
fetch('cfg.json')
    .then(response => response.json())
    .then(json => {
        roundsData = prepareRounds(json)
        renderTest(roundsData)
    })
    .catch(err => console.error("Could not load cfg.json", err))

function prepareRounds(json) {
    let rounds = []
    json.forEach((round, index) => {
        const x = Array.isArray(round.X)
            ? round.X[Math.floor(Math.random() * round.X.length)]
            : round.X;
        rounds.push({
            id: index,
            a: round.A,
            b: round.B,
            x: x,
        })
    })

    // In-Place
    shuffle(rounds)
    console.log(rounds)
    return rounds
}

function renderTest(rounds) {
    rounds.forEach((round, i) => {
        // Update timeline
        const stepLi = document.createElement('li')
        stepsContainer.insertBefore(stepLi, stepsContainer.lastElementChild)

        // Add form step
        const stepSection = document.createElement('section')
        stepSection.classList.add('form-step')
        stepSection.innerHTML = `
        <x-abx
            a="${round.a}"
            b="${round.b}"
            x="${round.x}"
        >
        </x-abx>
        `
        formContainer.insertBefore(stepSection, formContainer.lastElementChild)
    })

    updatePage(currentPage)
}

function validateCurrentStep() {
    const currentStepEl = formContainer.querySelectorAll('.form-step')[currentPage - 1]
    const abxComponent = currentStepEl.querySelector('x-abx')
    const totalPages = formContainer.querySelectorAll('.form-step').length

    if (currentPage === totalPages) {
        nextBtn.disabled = true
        nextBtn.setAttribute('data-disabled', 'true')
    }
    else if (!abxComponent) {
        nextBtn.disabled = false
        nextBtn.removeAttribute('data-disabled')
    } else {
        const hasAnswer = abxComponent.getResults() !== null
        nextBtn.disabled = !hasAnswer

        if (nextBtn.disabled) nextBtn.setAttribute('data-disabled', 'true')
        else nextBtn.removeAttribute('data-disabled')
    }
}

function updatePage(pageIndex) {
    // Pause all audios in the page
    document.querySelectorAll('x-abx').forEach(el => el.pauseInternal())

    // history.replaceState(null, null, `#${pageIndex}`);
    history.replaceState({}, '', `#${pageIndex}`)

    // Update timeline
    const totalSteps = stepsContainer.children.length
    const progressRatio = (pageIndex - 1) / (totalSteps - 1)
    progressLine.style.setProperty('--progress', progressRatio)

    // Update prev/next buttons
    prevBtn.disabled = (pageIndex === 1)
    validateCurrentStep()

    Array.from(stepsContainer.children).forEach((li, idx) => {
        if (idx + 1 === pageIndex) li.classList.add('active')
        else li.classList.remove('active')
    })

    const forms = formContainer.querySelectorAll('.form-step')
    forms.forEach((step, idx) => {
        if (idx + 1 === pageIndex) step.classList.add('active')
        else step.classList.remove('active')
    })
}

//
// NAVIGATION
//
document.addEventListener('answer-selected', () => {
    validateCurrentStep()
})
function goNext() {
    if (nextBtn.disabled) return

    const total = formContainer.querySelectorAll('.form-step').length;
    if (currentPage < total) {
        currentPage++
        updatePage(currentPage)
    }
}

function goPrev() {
    if (currentPage > 1) {
        currentPage--;
        updatePage(currentPage)
    }
}

nextBtn.addEventListener('click', goNext)
prevBtn.addEventListener('click', goPrev)

document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') goNext()
    if (e.key === 'ArrowLeft') goPrev()
})

// 
// SAVING
// 
const saveBtn = document.querySelector('#conclu button')
saveBtn.addEventListener('click', (e) => {
    e.preventDefault()

    let results = []
    document.querySelectorAll('x-abx').forEach((test, i) => {
        results.push({
            test: roundsData[i],
            result: test.getResults()
        })
    })
    const json = JSON.stringify(results, null, 2)
    const blob = new Blob([json], { type: "application/json" })
    console.log(json)

    // Ask for filename
    let filename = prompt("Please enter your name or ID for the file:", "subject_01")
    if (!filename) return
    if (!filename.endsWith('.json')) filename += '.json'

    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()

    setTimeout(() => {
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
    }, 0)
})