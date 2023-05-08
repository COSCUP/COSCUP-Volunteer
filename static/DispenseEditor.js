(function () {
    const tpl = /* html */`
<div class="dispense-editor">
    <b-modal class="dispense-modal" v-model="is_modal_opened" v-if="local_dispense" @close="close">
        <div class="modal-card">
            <div class="modal-card-head">
                <p class="modal-card-title">{{cta_label}}</p>
            </div>
            <div class="modal-card-body">
                <div class="content">
                    <div class="block">
                        <h4>
                            <span v-if="isCreate">確認</span>
                            選取的申請單
                        </h4>
                        <ol type="1">
                            <li v-for="expense in selected_expenses" :key="expense._id" class="mb-3">
                                <div class="is-flex is-align-items-center is-flex-wrap-wrap">
                                    <span class="mr-1">{{ users[expense.create_by].profile.badge_name }} 申請的</span>
                                    <span class="tag is-dark mr-1">{{ budgets[expense.request.buid].bid }}</span>
                                    <span class="mr-2">{{ budgets[expense.request.buid].name }}，金額為</span>
                                    <invoice-list class="mr-1 mb-0" :invoices="expense.invoices" />
                                    <span v-if="expense.request.paydate">，期望出款時間為 {{expense.request.paydate}} </span>
                                </div>
                            </li>
                        </ol>
                    </div>
                    <div class="block">
                        <h4>
                            <span v-if="isCreate">確認</span>
                            匯款資訊
                        </h4>
                        <ul>
                            <li>銀行代碼：<span class="is-family-monospace">{{ bank.code }}</span></li>
                            <li>銀行帳號：<span class="is-family-monospace">{{ bank.no }}</span></li>
                            <li>分行名稱：{{ bank.branch }}</li>
                            <li>戶名：{{ bank.name }}</li>
                        </ul>
                    </div>
                    <div class="block">
                        <h4>設定出款單資訊</h4>
                        <b-field label="預計出款日期">
                            <b-input type="date" v-model="local_dispense.dispense_date">
                        </b-field>
                        <template v-if="!isCreate">
                            <b-field label="出款階段">
                                <b-select v-model="local_dispense.status">
                                    <option
                                        v-for="status in dispense_status_list"
                                        :key="status.code"
                                        :value="status.code"
                                    >{{status.label}}</option>
                                </b-select>
                            </b-field>
                            <b-field label="出款單狀態">
                                <b-radio
                                    v-model="local_dispense.enable"
                                    name="enable"
                                    :disabled="!can_change_enable"
                                    :native-value="true"
                                >
                                    可使用
                                </b-radio>
                                <b-radio
                                    v-model="local_dispense.enable"
                                    name="enable"
                                    :disabled="!can_change_enable"
                                    :native-value="false"
                                >
                                    刪除
                                </b-radio>
                            </b-field>
                            <b-notification
                                type="is-warning"
                                has-icon
                                icon-size="is-small"
                                :active="!local_dispense.enable"
                                :closable="false"
                            >
                                將出款單設為<strong>刪除</strong>後，它的所有申請單，都會退回「審核中」，而且無法復原
                            </b-notification>
                        </template>
                    </div>
                </div>
            </div>
            <div class="modal-card-foot">
                <div class="field">
                    <div class="control">
                        <b-button type="is-link" :loading="is_applying_change" @click="create_or_update_dispense">{{cta_label}}</b-button>
                        <b-button type="is-warning" :loading="is_applying_change" @click="close">取消</b-button>
                    </div>
                </div>
            </div>
        </div>
    </b-modal>
</div>
`
    const AVAILABLE_DISPENSE_STATUS =  ['出款中', '已出款', '已完成']
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
                    return 'expense_ids' in val && 'dispense_date' in val
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
                is_applying_change: false
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
            dispense_status_list () {
                return this.statusList.filter(status => AVAILABLE_DISPENSE_STATUS.includes(status.label))
            },
            selected_expenses () {
                if (!this.local_dispense) {
                    return []
                }
                return this.local_dispense.expense_ids.map((id) => {
                    return this.allExpenses.find(exp => exp._id === id)
                })
            },
            bank () {
                if (this.selected_expenses.length) {
                    return this.selected_expenses[0].bank
                }
                return null
            },
            is_local_dispense_dirty () {
                return Object.entries(this.dispense).some(([key, value]) => {
                    return this.local_dispense[key] !== value
                })
            },
            can_be_deleted () {
                return this.dispense.enable
            },
            can_change_enable () {
                return this.dispense.enable
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
                this.$emit('close')
            },
            async create_or_update_dispense () {
                if (!this.is_local_dispense_dirty && !this.isCreate) {
                    this.close()
                    return
                }
                this.is_applying_change = true

                let payload = {}
                if (this.isCreate) {
                    payload = {
                        expense_ids: this.local_dispense.expense_ids,
                        dispense_date: this.local_dispense.dispense_date
                    }
                } else {
                    payload._id = this.local_dispense._id
                    Object.entries(this.local_dispense).forEach(([key, value]) => {
                        if (this.dispense[key] !== value) {
                            payload[key] = value
                        }
                    })
                }
                let resp
                try {
                    const casename = this.isCreate ? 'add' : 'update'
                    resp = await axios.post('/dispense/'+this.pid, {casename, data: payload})
                    this.$buefy.snackbar.open(`${this.cta_label}完畢`)
                } catch (err) {
                    this.$buefy.snackbar.open({
                        message: err.toString(),
                        type: 'is-error'
                    })
                }
                this.is_applying_change = false
                this.$emit('update')
                this.close()
            }
        }
    })
})()
