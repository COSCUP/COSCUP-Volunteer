(function () {
    const tpl = /* html */`
<div class="expense-editor">
    <b-modal
        v-if="local_expense && local_expense.request"
        v-model="is_modal_opened"
        @close="close"
    >
      <div class="modal-card">
          <header class="modal-card-head">
              <p class="modal-card-title">申請項目 - {{ budgets[local_expense.request.buid].name }} </p>
              <button class="delete" aria-label="close" @click="close"></button>
          </header>
          <section class="modal-card-body">
              <div class="content">
                  <div class="content">
                      <h4>預算表資訊</h4>
                      <table class="table is-bordered is-narrow is-striped">
                          <thead>
                              <tr>
                                  <th>項目</th>
                                  <th>名稱</th>
                              </tr>
                          </thead>
                          <tbody>
                              <tr>
                                  <td>預算表編號</td>
                                  <td><span class="tag is-dark">{{ budgets[local_expense.request.buid].bid }}</span></td>
                              </tr>
                              <!--
                              <tr>
                                  <td>組別 / 預算建立者</td>
                                  <td>
                                      <div class="field-body">
                                          <div class="field">
                                              <span class="select is-small">
                                                  <select v-model="local_expense.tid" disabled>
                                                      <option v-for="team in teams" :value="team.tid">{{ team.name }}</option>
                                                  </select>
                                              </span>
                                          </div>
                                          <div class="filed">
                                              <input class="input is-small" type="text" v-model="local_expense.uid" disabled>
                                          </div>
                                      </div>
                                  </td>
                              </tr>
                              -->
                              <tr>
                                  <td>預算名稱</td>
                                  <td>{{ budgets[local_expense.request.buid].name }}</td>
                              </tr>
                              <tr>
                                  <td>預算總金額</td>
                                  <td><span class="tag">{{ budgets[local_expense.request.buid].currency }}</span>
                                      <span>\${{ budgets[local_expense.request.buid].total.toLocaleString('en') }}</span></td>
                              </tr>
                              <tr>
                                  <td>預計支出時間</td>
                                  <td>{{ budgets[local_expense.request.buid].paydate }}</td>
                              </tr>
                              <tr>
                                  <td>說明</td>
                                  <td>{{ budgets[local_expense.request.buid].desc }}</td>
                              </tr>
                              <tr>
                                  <td>估算方式</td>
                                  <td>{{ budgets[local_expense.request.buid].estimate }}</td>
                              </tr>
                              <tr>
                                  <td>唯一編號</td>
                                  <td><span class="tag">{{ local_expense.code }}</span></td>
                              </tr>
                          </tbody>
                      </table>
                      <div class="content" v-if="local_expense.relevant_code.length > 0">
                          <h4>與其他申請單有關聯</h4>
                          <div class="tags">
                              <span class="tag is-link is-light" v-for="relevant in local_expense.relevant_code">{{ relevant }}</span>
                          </div>
                      </div>
                      <div class="content">
                          <h4>請款狀態</h4>
                          <div class="select">
                              <select v-model="local_expense.status">
                                  <option v-for="status in expense_status_list" :key="status.code" :value="status.code">
                                    {{ status.label }}
                                  </option>
                              </select>
                          </div>
                          <b-field label="預計出款日期" v-show="should_create_dispense">
                            <b-input type="date" v-model="dispense_date">
                          </b-field>
                      </div>
                      <div class="content">
                          <h4>請款說明</h4>
                          <p v-if="local_expense.request != undefined">
                              {{ local_expense.request.desc }}
                          </p>
                      </div>
                      <div class="content">
                          <h4>單據</h4>
                          <table class="table is-narrow is-hoverable">
                              <thead>
                                  <tr>
                                      <th>名稱</th>
                                      <th class="has-text-right">金額</th>
                                      <th>狀態</th>
                                      <th class="has-text-centered">已確認收到</th>
                                  </tr>
                              </thead>
                              <tbody>
                                  <tr v-for="invoice in local_expense.invoices">
                                      <td>{{ invoice.name }}</td>
                                      <td class="has-text-right is-family-monospace">
                                          {{ invoice.currency }} \${{ invoice.total.toLocaleString('en') }}
                                      </td>
                                      <td>
                                          <span v-if="invoice.status === 'not_send'" class="tag is-warning">還未寄出</span>
                                          <span v-if="invoice.status === 'sent'" class="tag is-success is-light">已寄出</span>
                                          <span v-if="invoice.status === 'no_invoice'" class="tag is-info is-light">無單據</span>
                                      </td>
                                      <td class="has-text-centered">
                                          <label class="checkbox">
                                              <input type="checkbox" v-model="invoice.received">
                                          </label>
                                      </td>
                                  </tr>
                              </tbody>
                          </table>
                      </div>
                      <div class="content" v-if="local_expense.bank">
                          <h4>匯款資訊</h4>
                          <ul>
                              <li>銀行代碼：<span class="is-family-monospace">{{ local_expense.bank.code }}</span></li>
                              <li>銀行帳號：<span class="is-family-monospace">{{ local_expense.bank.no }}</span></li>
                              <li>分行名稱：{{ local_expense.bank.branch }}</li>
                              <li>戶名：{{ local_expense.bank.name }}</li>
                          </ul>
                      </div>
                      <div class="content">
                          <h4>申請單狀態</h4>
                          <div class="select">
                              <select v-model="local_expense.enable">
                                  <option :value='true'>可使用</option>
                                  <option :value='false'>已刪除</option>
                              </select>
                          </div>
                      </div>
                  </div>
              </div>
              <form @submit.prevent="to_update">
                  <div class="field">
                      <div class="control">
                          <button class="button is-link" type="submit" :class="{'is-loading': local_expense.is_loading}">
                              {{cta_label}}
                          </button>
                          <button class="button is-warning" @click="close" :class="{'is-loading': local_expense.is_loading}">取消</button>
                      </div>
                  </div>
              </form>
          </section>
          <footer class="modal-card-foot">
          </footer>
      </div>
    </b-modal>
</div>
`
    const AVAILABLE_EXPENSE_STATUS = ['已申請', '審核中', '出款中']
    Vue.component('expense-editor', {
        template: tpl,
        props: {
            pid: {
                type: String,
                required: true
            },
            expense: {
                type: Object,
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
            teams: {
                type: Array,
                required: true
            },
            statusList: {
                type: Array,
                required:true
            }
        },
        data () {
            return {
                local_expense: null,
                dispense_date: '',
                is_modal_opened: false
            }
        },
        computed: {
            expense_status_list () {
                return this.statusList.filter(status => AVAILABLE_EXPENSE_STATUS.includes(status.label))
            },
            should_create_dispense () {
                return this.local_expense.status === '3' && // 出款中
                    this.local_expense.status !== this.expense.status
            },
            cta_label () {
                if (this.should_create_dispense) {
                    return '更新，並建立出款單'
                }
                return '更新'
            }
        },
        watch: {
            expense (new_val) {
                this.reset_editor(new_val)
            }
        },
        methods: {
            reset_editor (item) {
                this.local_expense = Object.assign({}, item, {is_edit: true});
                // default set dispense after 10 days
                this.dispense_date = dayjs().add(10, 'days').format('YYYY-MM-DD')
                this.is_modal_opened = true
            },
            close () {
                this.is_modal_opened = false
                this.local_expense = null
                this.$emit('close')
            },
            async to_update () {
                await axios.post('./'+this.pid, {casename: 'update', data: this.local_expense})
                if (this.should_create_dispense) {
                    const payload = {
                        expense_ids: [this.local_expense._id],
                        dispense_date: this.dispense_date
                    }
                    await axios.post('/dispense/'+this.pid, {casename: 'add', data: payload})
                }
                this.$emit('update')
                this.close()
            }
        }
    })
})()