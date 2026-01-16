class ABX extends HTMLElement {

    constructor() {
        super()
        this.shadow = this.attachShadow({ mode: "open" })
        this.id = Math.random().toString(16).slice(2)
    }

    connectedCallback() {
        this.render()
        this.addEventListeners()
    }

    addEventListeners() {
        this.shadow.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => this.handlePlayClick(btn));
        })

        this.shadow.querySelectorAll('input[type="radio"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.dispatchEvent(new CustomEvent('answer-selected', {
                    bubbles: true,
                    composed: true
                }))
            })
        })
    }

    render() {
        this.shadow.innerHTML = `
    <p>Which violin is X?</p>
    <div id="controls">
        <button>A<audio src="${this.getAttribute('a')}" preload="auto"></audio></button>

        <span></span>
        
        <button>B<audio src="${this.getAttribute('b')}" preload="auto"></audio></button>
        

        <input type="radio" id="choiceA-${this.uniqueId}" name="choice-${this.id}" value="A" />
        <label for="choiceA-${this.uniqueId}">X is A</label>
        <button>X<audio src="${this.getAttribute('x')}" preload="auto"></audio></button>
        <input type="radio" id="choiceB-${this.uniqueId}" name="choice-${this.id}" value="B" />
        <label for="choiceB-${this.uniqueId}">X is B</label>
    </div>
    <link rel="stylesheet" href="css/xabx.css">
        `
    }

    handlePlayClick(button) {
        const audio = button.querySelector('audio')
        let paused = audio.paused

        document.querySelectorAll('x-abx').forEach(el => el.pauseInternal())

        if (paused) {
            audio.currentTime = 0
            audio.play()
        } else {
            audio.pause()
        }

        this.shadow.querySelectorAll('button').forEach(b => b.classList.remove('active'))
        button.classList.add('active')
        audio.onended = () => button.classList.remove('active')
    }

    pauseInternal() {
        this.shadow.querySelectorAll('audio').forEach(audio => audio.pause())
        this.shadow.querySelectorAll('button').forEach(b => b.classList.remove('active'))
    }

    getResults() {
        const checked = this.shadow.querySelector('input[type=radio]:checked')
        return checked ? checked.value : null
    }

}

customElements.define('x-abx', ABX)