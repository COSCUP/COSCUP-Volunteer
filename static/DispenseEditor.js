(function () {
    const tpl = /* html */`
<div class="dispense-editor">
    <b-modal class="dispense-modal" v-model="is_modal_opened" v-if="local_dispense">
        <div class="modal-card">
            <div class="modal-card-head">
                <p class="modal-card-title">{{cta_label}}</p>
            </div>
            <div class="modal-card-body">
                <div class="content">
                    <div class="block">
                        <h4>設定出款單資訊</h4>
                        <b-field label="預計出款日期">
                            <b-input type="date" v-model="local_dispense.dispense_at">
                        </b-field>
                    </div>
                    <div class="block">
                        <h4>確認選取的申請單</h4>
                        <ol type="1">
                            <li v-for="expense in selected_expenses" :key="expense._id">
                                <div class="is-flex is-align-items-center">
                                    <span class="mr-1">{{ users[expense.create_by].profile.badge_name }} 申請的</span>
                                    <span class="tag is-dark mr-1">{{ budgets[expense.request.buid].bid }}</span>
                                    <span class="mr-2">{{ budgets[expense.request.buid].name }}，金額為</span>
                                    <div class="tags has-addons mr-1 mb-0" v-for="invoice in expense.invoices">
                                        <span class="tag is-info">{{ invoice.currency }}</span>
                                        <span class="tag is-success is-light">\${{ invoice.total.toLocaleString() }}</span>
                                    </div>
                                    <span>，期望出款時間為 {{expense.request.paydate}} </span>
                                </div>
                            </li>
                        </ol>
                    </div>
                    <div class="block">
                        <h4>確認匯款資訊</h4>
                        <ul>
                            <li>銀行代碼：<span class="is-family-monospace">{{ bank_of_selected_expense.code }}</span></li>
                            <li>銀行帳號：<span class="is-family-monospace">{{ bank_of_selected_expense.no }}</span></li>
                            <li>分行名稱：{{ bank_of_selected_expense.branch }}</li>
                            <li>戶名：{{ bank_of_selected_expense.name }}</li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="modal-card-foot">
                <div class="field">
                    <div class="control">
                        <b-button type="is-link" :loading="is_creating_dispense" @click="create_dispense">{{cta_label}}</b-button>
                        <b-button type="is-warning" :loading="is_creating_dispense" @click="close">取消</b-button>
                    </div>
                </div>
            </div>
        </div>
    </b-modal>
</div>
`
    Vue.component('dispense-editor', {
        template: tpl,
        props: {
            pid: {
                type: String,
                required: true
            },
            allExpenses: {
                type: Array,
                required: true
            },
            dispense: {
                type: Object,
                required: true,
                validator (val) {
                    return 'expense_ids' in val && 'dispense_at' in val
                }
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
            isCreate: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                local_dispense: null,
                is_modal_opened: false,
                is_creating_dispense: false
            }
        },
        computed: {
            cta_label () {
                if (this.isCreate) {
                    return '建立出款單'
                } else {
                    return '修改出款單'
                }
            },
            selected_expenses () {
                if (!this.local_dispense) {
                    return []
                }
                return this.local_dispense.expense_ids.map((id) => {
                    return this.allExpenses.find(exp => exp._id === id)
                })
            },
            bank_of_selected_expense () {
                if (this.selected_expenses.length) {
                    return this.selected_expenses[0].bank
                }
                return null
            }
        },
        watch: {
            dispense (new_val) {
                this.reset_editor(new_val)
            }
        },
        methods: {
            reset_editor (item) {
                if (item) {
                    this.local_dispense = { ...item }
                    this.is_modal_opened = true
                }
            },
            close () {
                this.is_modal_opened = false
                this.local_dispense = null
            },
            async create_dispense () {
                // TODO: support update
                this.is_creating_dispense = true
                const payload = {
                    expense_ids: this.local_dispense.expense_ids,
                    dispense_at: this.local_dispense.dispense_at
                }
                let resp
                try {
                    resp = await axios.post('/dispense/'+this.pid, {casename: 'add', data: payload})
                    this.$buefy.snackbar.open('出款單建立完畢')
                } catch (err) {
                    this.$buefy.snackbar.open({
                        message: err.toString(),
                        type: 'is-error'
                    })
                }
                this.is_creating_dispense = false
                this.$emit('update')
                this.close()
            }
        }
    })
})()
