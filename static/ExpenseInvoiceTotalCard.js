(function () {
    const template = /* html */`
<div class="field has-background-link-light p-3">
<label class="label">{{ label }}</label>
<div class="field is-grouped is-grouped-multiline">
    <div class="control">
        <div class="tags has-addons" v-for="[currency, total] in Object.entries(invoicesTotal)">
            <span class="tag is-info">{{ currency }}</span>
            <span class="tag is-success is-light">{{ total }}</span>
        </div>
    </div>
</div>
`
    Vue.component('expense-invoice-total-card', {
        template,
        props: {
            label: {
                type: String,
                require: true,
            },
            /**
             * typeof invoice_total = {
             *     TWD: number,
             *     USD: number,
             * }
             */
            invoicesTotal: {
                type: Object,
                require: true,
            }
        }
    })
})()
