(function () {
    const tpl = `
        <div :class="labelClass" :role="role">
            <span class="icon"><i :class="iconClass"></i></span>
            <span>{{ labelMeta.label }}</span>
        </div>`
    const statusMetaMap = {
        // as this is the only place to define color & icon for each status code
        // there's no way to migrate it back to expense model or module
        // as the result, no need to pass status from expense view :p
        1: { color: 'is-warning', icon: 'hand-paper', label: '已申請' },
        2: { color: 'is-link', icon: 'bolt', label: '審核中' },
        3: { color: 'is-primary', icon: 'hand-holding-usd', label: '出款中' },
        4: { color: 'is-success', icon: 'stamp', label: '已出款' },
        5: { color: 'is-success', icon: 'clipboard-check', label: '已完成' },
        disable: { color: 'is-danger', icon: 'ban', label: '已刪除' },
        unknown: { color: 'is-danger', icon: 'ban', label: '不明狀態' }
    }
    Vue.component('expense-status-label', {
      props: {
        item: {
            type: Object,
            required: true
        },
        role: {
            type: String,
            default: ''
        }
      },
      computed: {
        labelClass () {
            return [this.labelMeta.color]
        },
        iconClass () {
            return ['fas', `fa-${this.labelMeta.icon}`]
        },
        labelMeta () {
            const statusCode = this.item.status
            if (statusCode in statusMetaMap) {
                return statusMetaMap[statusCode]
            } else if (!this.item.enable) {
                return statusMetaMap.disable
            }
            // always return sth, so we know sth goes wrong
            return statusMetaMap.unknown
        }
      },
      template: tpl
    })
})()
