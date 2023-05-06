(function () {
    const tpl = /* html */`
<div class="dispense-table">
    <b-table class="is-fullwidth" :data="rich_dispenses" detailed>
        <b-table-column field="status" label="狀態" v-slot="props">
            <expense-status-label class="tag" :status-code="props.row.status"></expense-status-label>
        </b-table-column>
        <b-table-column field="dispense_date" label="（預計）出款日期" v-slot="props">
            {{props.row.dispense_date}}
        </b-table-column>
        <b-table-column field="invoice_sum" label="總計金額" v-slot="props">
            <invoice-list :invoices="props.row.invoice_sum" />
        </b-table-column>
        <b-table-column field="bank" label="匯款資訊" v-slot="props">
            <p>{{props.row.bank.code}}-{{props.row.bank.branch}}-{{props.row.bank.no}}</p>
            <strong>{{props.row.bank.name}}</strong>
        </b-table-column>
        <b-table-column label="部門" v-slot="props">
            {{unique_items(props.row.expenses, 'tid').join('、')}}
        </b-table-column>
        <b-table-column label="申請人" v-slot="props">
            <div class="is-flex is-align-items-center">
                <user-badge v-for="id in unique_items(props.row.expenses, 'create_by')" :users="users" :id="id" />
            </div>
        </b-table-column>
        <b-table-column label="" v-slot="props" width="3rem" v-if="isAdmin">
            <b-button @click="start_edit_dispense(props.row)">編輯出款單</b-button>
        </b-table-column>
        <template #detail="props">
            <expense-table
                class="notification"
                :expenses="props.row.expenses"
                :budgets="budgets"
                :users="users"
                :is-nested="true"
                :is-admin="isAdmin"
                :me="me"
                @edit="edit_expense"
            ></expense-table>
        </template>
    </b-table>
    <dispense-editor
      v-if="isAdmin"
      :pid="pid"
      :all-expenses="allExpenses"
      :dispense="dispense_to_edit"
      :budgets="budgets"
      :users="users"
      :status-list="statusList"
      @update="$emit('update')"
      @close="dispense_to_edit = null"
    ></dispense-editor>
</div>
`

    Vue.component('dispense-table', {
        template: tpl,
        props: {
            allExpenses: {
                type: Array,
                required: true
            },
            dispenses: {
                type: Array,
                required: true
            },
            budgets: {
                type: Object,
                required: true
            },
            users: {
                type: Object,
                required: true
            },
            statusList: {
                type: Array,
                required:true
            },
            pid: {
                type: String,
                default: 0
            },
            isAdmin: {
                type: Boolean,
                default: true
            },
            me: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                dispense_to_edit: null
            }
        },
        computed: {
            rich_dispenses () {
                return this.dispenses.map((dispense) => {
                    const ret = { ...dispense }
                    ret.expenses = dispense.expense_ids.map((id) => {
                        return this.allExpenses.find(item => item._id === id)
                    })
                    const invoices = ret.expenses.reduce((sum, expense) => {
                        expense.invoices.forEach(({ currency, total }) => {
                            if (!sum[currency]) {
                                sum[currency] = 0
                            }
                            sum[currency] += total
                        })
                        return sum
                    }, {})
                    ret.invoice_sum = Object.entries(invoices).map(([currency, total]) => {
                        return { currency, total }
                    })
                    ret.bank = ret.expenses[0].bank
                    return ret
                })
            }
        },
        methods: {
            unique_items (item_list, key) {
                const unique_items = item_list.reduce((unique, item) => {
                    const value = key ? item[key] : item
                    unique.add(value)
                    return unique
                }, new Set())
                return [...unique_items]
            },
            start_edit_dispense (dispense) {
                this.dispense_to_edit = dispense
            },
            edit_expense (expense) {
                this.$emit('edit-expense', expense)
            }
        }
    })
})()
