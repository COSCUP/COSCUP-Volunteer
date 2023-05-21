(function () {
    const tpl = /* html */`
<div class="expense-table">
    <table class="table is-fullwidth">
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
                <th v-if="!isNested">狀態</th>
                <th>預算編號</th>
                <th v-if="isAdmin">預算唯一編號</th>
                <th v-if="isAdmin">部門</th>
                <th v-if="should_show_owner">申請人</th>
                <th>金額</th>
                <th>期望出款時間</th>
                <th v-if="is_some_editable" />
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
                <td v-if="!isNested" class="is-vcentered">
                    <expense-status-label class="tag is-clickable" @click="edit(item)" :item="item"></expense-status-label>
                </td>
                <td class="is-vcentered">
                    <span class="tag is-dark">{{ budgets[item.request.buid].bid }}</span>
                    <span><a @click="edit(item)">{{ budgets[item.request.buid].name }}</a></span>
                </td>
                <td v-if="isAdmin" class="is-vcentered">
                    <span class="tag is-success is-light">{{ item.request.code }}</span>
                </td>
                <td v-if="isAdmin" class="is-vcentered">{{ item.tid }}</td>
                <td v-if="should_show_owner" class="is-vcentered">
                    <user-badge :id="item.create_by" :users="users" />
                </td>
                <td class="is-vcentered">
                    <div class="field is-grouped">
                        <div class="control">
                            <div class="tags has-addons">
                                <span class="tag is-dark"><span class="icon"><i class="fas fa-file-invoice-dollar"></i></span></span>
                                <span class="tag is-link is-light">{{ item.invoices.length }}</span>
                            </div>
                        </div>
                        <invoice-list :invoices="item.invoices" />
                    </div>
                </td>
                <td class="is-vcentered">{{ item.request.paydate }}</td>
                <td class="is-vcentered" v-if="is_editable(item)">
                    <b-button @click="edit(item)">編輯申請單</b-button>
                </td>
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
                default () {
                    return {}
                }
            },
            isSelectable: {
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
            },
            isAdmin: {
                type: Boolean,
                default: true
            },
            isNested: {
                type: Boolean,
                default: false
            },
            me: {
                type: String,
                default: ''
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
            is_some_editable () {
                return this.isAdmin || this.expenses.some(exp => exp.create_by === this.me)
            },
            should_show_owner () {
                return this.isAdmin || this.isNested
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
            is_editable (expense) {
                return this.isAdmin || expense.create_by === this.me
            },
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
                if (this.is_editable(item)) {
                    this.$emit('edit', item)
                }
            }
        }
    })
})()