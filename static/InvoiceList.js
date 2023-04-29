(function () {
    const tpl = /* html */`
<div class="is-flex is-align-items-center">
    <div class="tags has-addons" v-for="invoice in invoices" :key="invoice.currency">
        <span class="tag is-info">{{ invoice.currency }}</span>
        <span class="tag is-success is-light">\${{ invoice.total.toLocaleString('en') }}</span>
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
