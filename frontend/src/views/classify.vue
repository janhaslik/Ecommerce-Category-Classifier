<template>
    <div class="classify-page">
        <h1>Category Classifier</h1>
        <div class="classify-view">
            <div class="input">
                <h2>Enter Description</h2>
                <textarea v-model="text" class="prompt" placeholder="Enter your Description..."></textarea>
                <button type="submit" @click="classify()" class="btn">Classify</button>
            </div>
            <div class="output" v-if="labels.length">
                <li v-for="(label) in labels" :key="label.category" class="output-label label"
                    @click="selectChoice(label)">
                    <div class="success-animation" v-if="label.chosen">
                        <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
                            <circle class="checkmark__circle" cx="26" cy="26" r="25" fill="none" />
                            <path class="checkmark__check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8" />
                        </svg>
                    </div>
                    <span>{{ label.category }}</span>
                    <div class="single-chart">
                        <svg viewBox="0 0 36 36" :class="`circular-chart ${getColorClass(label.probability)}`">
                            <path class="circle-bg" d="M18 2.0845
                                        a 15.9155 15.9155 0 0 1 0 31.831
                                        a 15.9155 15.9155 0 0 1 0 -31.831" />
                            <path class="circle" :stroke-dasharray="`${label.probability * 100}, 100`" d="M18 2.0845
                                        a 15.9155 15.9155 0 0 1 0 31.831
                                        a 15.9155 15.9155 0 0 1 0 -31.831" />
                            <text x="18" y="20.35" class="percentage">{{ (label.probability * 100).toFixed(0) }}%</text>
                        </svg>
                    </div>

                </li>
            </div>

        </div>
    </div>
</template>

<script lang="ts">
interface category_label {
    category: string;
    probability: number;
    chosen?: boolean
}


export default {
    data() {
        return {
            labels: [] as category_label[],
            predictionid: -1,
            text: "",
            lockSelect: false,
        }
    },
    watch: {
        labels() {
            this.labels.sort((a, b) => b.probability - a.probability);
        }
    },
    mounted() {
    },
    methods: {
        getColorClass(prob: number) {
            if (prob <= 0.25) return 'red';
            if (prob <= 0.50) return 'orange';
            if (prob <= 0.75) return 'light-green';
            return 'green';
        },
        async classify() {
            //API
            //ASK AI for classification
            this.lockSelect = false;
            const classifyReqObject = { 'text': this.text }

            let res;
            if (import.meta.env.VITE_DEVMODE=='true') {
                res = {
                    predictionid: 1, categories_probabilities: [
                        { category: "Electronics", probability: "0.99" },
                        { category: "Household", probability: "0.75" },
                        { category: "Books", probability: "0.50" },
                        { category: "Clothing & Accessories", probability: "0.25" }]
                }
            }
            else {
                res = await (await fetch('/api/classify', {
                    method: 'POST',
                    headers: { "content-type": "application/json" },
                    body: JSON.stringify(classifyReqObject)
                })).json()
            }


            this.predictionid = res.predictionid
            res.categories_probabilities.forEach((m: any) => m.probability = parseFloat(m.probability))
            this.labels = res.categories_probabilities
        },
        async selectChoice(label: category_label) {
            //API
            //PATCH selected label
            //GET newest RHLF list
            if (this.lockSelect) return;
            this.labels[this.labels.findIndex(l => l.category == label.category)].chosen = true;
            this.lockSelect = true;
            const feedbackReqObject = { 'category': label.category }

            if (import.meta.env.VITE_DEVMODE=='false') {
                await fetch(`/api/feedback/${this.predictionid}`, {
                    method: "PATCH",
                    headers: { "content-type": "application/json" },
                    body: JSON.stringify(feedbackReqObject)
                })

            }
        }

    }
}
</script>

<style scoped>
.flex {
    display: flex;
}

.ct {
    justify-content: center;
}


.success-animation {
    width: 100%;
    justify-content: right;
    display: flex;
}

.checkmark {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    stroke-width: 2;
    stroke: #4bb71b;
    stroke-miterlimit: 10;
    box-shadow: inset 0px 0px 0px #4bb71b;
    animation: fill .4s ease-in-out .4s forwards, scale .3s ease-in-out .9s both;
    margin: 0 1rem;

}

.checkmark__circle {
    stroke-dasharray: 166;
    stroke-dashoffset: 166;
    stroke-width: 2;
    stroke-miterlimit: 10;
    stroke: #4bb71b;
    fill: #fff;
    animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
}

.checkmark__check {
    transform-origin: 50% 50%;
    stroke-dasharray: 48;
    stroke-dashoffset: 48;
    animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
}

.classify-page {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100vh;
    margin: 0;

}

.classify-view {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 50vh;
    transition: linear 1s;
    margin-top: 5em;
}

.input {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 0.5em;
    width: 30em;
    margin-bottom: 2em;
}

.input h2 {
    text-align: center;
}


.input button {
    width: 20em;
}


.prompt {
    text-decoration: none;
    width: 20em;
    height: 10em;
    margin-top: 0.5em;
    padding: 10px 18px;
}

.output,
.skelleton {
    width: 30em;
    padding: 1rem;
}

.output-label {
    flex-direction: row-reverse;
    justify-content: start;
    align-items: center;
    cursor: pointer;
    user-select: none;
}

.label {
    box-shadow: 0 2px 3px rgba(0, 0, 0, .5);
    display: flex;
    padding: 0.5rem;
    margin: 0.2rem;
}

.output-label:hover {
    box-shadow: 0 2px 5px rgba(0, 0, 0, .7);

}

.output-label span {
    font-size: 20px;
    font-weight: bold;
}

.flex-wrapper {
    display: flex;
    flex-flow: row nowrap;
}

.single-chart {
    min-width: 33%;
}

.circular-chart {
    display: block;
    margin: 10px auto;
    max-width: 50%;
    max-height: 75px;
}

.circle-bg {
    fill: none;
    stroke: #eee;
    stroke-width: 3.8;
}

.circle {
    fill: none;
    stroke-width: 2.8;
    stroke-linecap: round;
    animation: progress 2s ease-out forwards;
}


.circular-chart.red .circle {
    stroke: #ff0000;
}

.circular-chart.orange .circle {
    stroke: #ff9f00;
}

.circular-chart.light-green .circle {
    stroke: #9acd32;
}

.circular-chart.green .circle {
    stroke: #4CC790;
}

.percentage {
    fill: #666;
    font-family: sans-serif;
    font-size: 0.5em;
    text-anchor: middle;
}

/* KEYFRAMES */

@keyframes stroke {
    100% {
        stroke-dashoffset: 0;
    }
}

@keyframes scale {

    0%,
    100% {
        transform: none;
    }

    50% {
        transform: scale3d(1.1, 1.1, 1);
    }
}

@keyframes scale2 {

    0% {
        transform: scale(1, 0);
    }

    100% {
        transform: scale(1, 1);
    }
}

@keyframes fill {
    100% {
        box-shadow: inset 0px 0px 0px 30px #4bb71b;
    }
}


@keyframes progress {
    0% {
        stroke-dasharray: 0 100;
    }
}
</style>
