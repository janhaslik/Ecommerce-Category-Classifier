<template>
    <div class="finetune-page">
        <div id="RHLF-container" v-if="RHLF_list.length">
            <div class="RHLF-list">
                <table>

                    <tr>
                        <th>Text</th>
                        <th>Predicted</th>
                        <th>Corrected</th>
                    </tr>
                    <tr v-for="item in RHLF_list">
                        <td width="40%"> <code>{{ item.input_text }}</code></td>
                        <td width="30%">{{ item.predicted_category }}</td>
                        <td width="30%">{{ item.feedback_category }}</td>
                    </tr>

                </table>
            </div>
            <div class="flex ct">
                <button class="btn" @click="finetune()">Finetune Model</button>
            </div>
        </div>
    </div>
</template>

<script lang="ts">

interface feedback_entry {
    feedback_category: String;
    predicted_category: String;
    input_text: String;
}

export default {
    data() {
        return {
            RHLF_list: [] as feedback_entry[],
        }
    },
    async mounted() {
        if (import.meta.env.VITE_DEVMODE=='false') {
            const res = await (await fetch(`api/feedback`, {
                method: "GET"
            })).json()
            this.RHLF_list = res.feedback
        } else {

            this.RHLF_list = [{ "input_text": "tomato tomato tomato tomato tomato tomato tomato ", "predicted_category": "Books", "feedback_category": "Household" },
            { "input_text": "guacamole", "predicted_category": "Books", "feedback_category": "Household" },
            { "input_text": "microsoft", "predicted_category": "Electronics", "feedback_category": "Electronics" },
            { "input_text": "noBook", "predicted_category": "Books", "feedback_category": "Household" },
            { "input_text": "Appel", "predicted_category": "Electronics", "feedback_category": "Household" },
            { "input_text": "Windows", "predicted_category": "Electronics", "feedback_category": "Electronics" },
            { "input_text": "NOR", "predicted_category": "Books", "feedback_category": "Electronics" },
            { "input_text": "Knife", "predicted_category": "Household", "feedback_category": "Household" },
            { "input_text": "Monitor", "predicted_category": "Clothing & Accessories", "feedback_category": "Electronics" },

            { "input_text": "tomato", "predicted_category": "Books", "feedback_category": "Household" },
            { "input_text": "guacamole", "predicted_category": "Books", "feedback_category": "Household" },
            { "input_text": "microsoft", "predicted_category": "Electronics", "feedback_category": "Electronics" },
            { "input_text": "noBook", "predicted_category": "Books", "feedback_category": "Household" },
            { "input_text": "Appel", "predicted_category": "Electronics", "feedback_category": "Household" },
            { "input_text": "Windows", "predicted_category": "Electronics", "feedback_category": "Electronics" },
            { "input_text": "NOR", "predicted_category": "Books", "feedback_category": "Electronics" },
            { "input_text": "Knife", "predicted_category": "Household", "feedback_category": "Household" },
            { "input_text": "Monitor", "predicted_category": "Clothing & Accessories", "feedback_category": "Electronics" },

            { "input_text": "tomato", "predicted_category": "Books", "feedback_category": "Household" },
            { "input_text": "guacamole", "predicted_category": "Books", "feedback_category": "Household" },
            { "input_text": "microsoft", "predicted_category": "Electronics", "feedback_category": "Electronics" },
            { "input_text": "noBook", "predicted_category": "Books", "feedback_category": "Household" },
            { "input_text": "Appel", "predicted_category": "Electronics", "feedback_category": "Household" },
            { "input_text": "Windows", "predicted_category": "Electronics", "feedback_category": "Electronics" },
            { "input_text": "NOR", "predicted_category": "Books", "feedback_category": "Electronics" },
            { "input_text": "Knife", "predicted_category": "Household", "feedback_category": "Household" },
            { "input_text": "Monitor", "predicted_category": "Clothing & Accessories", "feedback_category": "Electronics" },
            ]
        }
    },
    methods: {
        async finetune() {
            //API 
            //POST newest RHLF onto AI

            if (import.meta.env.VITE_DEVMODE=='false') {
                await fetch(`/api/finetune`, { method: "POST" })
            }
        }
    }
}
</script>

<style scoped>
#RHLF-container {
    height: 90%;
    width: 90%;
    margin: 1rem
}

.RHLF-list {
    overflow: hidden auto;
    max-height: calc(100% - 20px - 75px);
    scrollbar-width: thin;
    box-shadow: 0 2px 3px rgba(0, 0, 0, .5);
    border-radius: 1rem;
}

.RHLF-list table {
    width: 100%;
}

.RHLF-list tr * {
    padding: 5px;
}

.RHLF-list tr {
    box-shadow: 1px 1px 1px black;
}

.RHLF-list tr:nth-child(2n) {
    background-color: rgb(240, 240, 240);
}

.RHLF-list th {
    background-color: rgb(0, 152, 121);
    color: white;
}

.finetune-page {
    display: flex;
    flex-direction: column;
    justify-content: start;
    align-items: center;
    width: 100%;
    height: 100vh;
    margin: 0;

}

.btn {
    width: 20em;
}
</style>