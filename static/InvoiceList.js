(function () {
    const tpl = /* html */`
<div class="field is-grouped">
    <div class="control" v-for="invoice in invoices" :key="invoice.currency">
        <div class="tags has-addons">
            <span class="tag is-info">{{ invoice.currency }}</span>
            <span class="tag is-success is-light">\${{ invoice.total.toLocaleString('en') }}</span>
        </div>
    </div>
</div>
`
    Vue.component('invoice-list', {
        template: tpl,
        props: {
            invoices: {
                type: Array,
                required: true
            }
        }
    })
})()
