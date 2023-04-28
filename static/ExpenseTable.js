(function () {
    const tpl = /* html */`
<div class="expense-table">
    <div class="notification is-primary" v-if="is_table_empty">
        <span v-if="isLoading"> 申請單讀取中 </span>
        <span v-else> 這類申請單被吃光光了 😐 </span>
    </div>
    <table class="table is-fullwidth" v-else>
        <thead>
            <tr>
                <th v-if="isSelectable">
                  <label class="checkbox">
                    <input
                      type="checkbox"
                      :checked="is_all_expense_selected"
                      @input="toggle_all_expense"
                    >
                  </label>
                </th>
                <th>申請單號</th>
                <th>狀態</th>
                <th>預算編號</th>
                <th>預算唯一編號</th>
                <th>部門</th>
                <th></th>
                <th>申請人</th>
                <th>金額</th>
                <th>期望出款時間</th>
            </tr>
        </thead>
        <tbody>
            <tr
              v-for="item in expenses"
              :key="item._id"
              :class="{'is-delete': item.enabled === false, 'is-selected': is_expense_selected(item)}"
            >
                <td class="is-vcentered" v-if="isSelectable">
                  <label class="checkbox">
                    <input
                      type="checkbox"
                      :checked="is_expense_selected(item)"
                      @input="toggle_expense(item)"
                    >
                  </label>
                </td>
                <td class="is-vcentered">
                    <p><span class="tag is-link is-light">{{ item.code }}</span></p>

                    <p class="is-size-7">{{ new Date(item.create_at).toLocaleString() }}</p>
                </td>
                <td class="is-vcentered">
                    <expense-status-label class="tag is-clickable" @click="edit(item)" :item="item"></expense-status-label>
                </td>
                <td class="is-vcentered">
                    <span class="tag is-dark">{{ budgets[item.request.buid].bid }}</span>
                    <span><a @click="edit(item)">{{ budgets[item.request.buid].name }}</a></span>
                </td>
                <td class="is-vcentered">
                    <span class="tag is-success is-light">{{ item.request.code }}</span>
                </td>
                <td class="is-vcentered">{{ item.tid }}</td>
                <td class="is-vcentered">
                    <a :href="'/user/'+ item.create_by">
                        <figure class="image is-32x32"><img class="is-rounded" :src="users[item.create_by].oauth['picture']"></figure>
                    </a>
                </td>
                <td class="is-vcentered">
                    <a :href="'/user/'+ item.create_by">
                        {{ users[item.create_by].profile.badge_name }}
                    </a>
                </td>
                <td class="is-vcentered">
                    <div class="field is-grouped is-grouped-multiline">
                        <div class="control">
                            <div class="tags has-addons">
                                <span class="tag is-dark"><span class="icon"><i class="fas fa-file-invoice-dollar"></i></span></span>
                                <span class="tag is-link is-light">{{ item.invoices.length }}</span>
                            </div>
                        </div>
                        <div class="control" v-for="invoice in item.invoices">
                            <div class="tags has-addons">
                                <span class="tag is-info">{{ invoice.currency }}</span>
                                <span class="tag is-success is-light">\${{ invoice.total.toLocaleString('en') }}</span>
                            </div>
                        </div>
                    </div>
                </td>
                <td class="is-vcentered">{{ item.request.paydate }}</td>
            </tr>
        </tbody>
    </table>
</div>
`
    Vue.component('expense-table', {
        template: tpl,
        props: {
            expenses: {
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
            isSelectable: {
                type: Boolean,
                default: false
            },
            isEditable: {
                type: Boolean,
                default: false
            },
            isLoading: {
                type: Boolean,
                default: false
            },
            selectedExpense: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                local_selected_expense: this.selectedExpense
            }
        },
        computed: {
            is_all_expense_selected () {
                // local_selected_expense will be reset every time when expenses changed
                return this.expenses.length === this.local_selected_expense.length
            },
            is_table_empty () {
                return this.isLoading || !this.expenses.length
            }
        },
        watch: {
            expenses () {
                this.reset_page_state()
            },
            local_selected_expense (new_val) {
                this.$emit('update:selectedExpense', new_val)
            },
            selectedExpense (new_val) {
                this.local_selected_expense = new_val
            }
        },
        methods: {
            is_expense_selected (expense) {
                return this.local_selected_expense.indexOf(expense) >= 0
            },
            toggle_expense (expense) {
                const index = this.local_selected_expense.indexOf(expense)
                if (index >= 0) {
                    this.local_selected_expense.splice(index, 1)
                } else {
                    this.local_selected_expense.push(expense)
                }
            },
            toggle_all_expense () {
                if (this.is_all_expense_selected) {
                    this.local_selected_expense = []
                } else {
                    this.local_selected_expense = this.expenses.slice()
                }
            },
            reset_page_state () {
                this.local_selected_expense = []
            },
            edit (item) {
                if (this.isEditable) {
                    this.$emit('edit', item)
                }
            }
        }
    })
})()