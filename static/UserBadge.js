(function () {
    const tpl = /* html */`
<a class="user-badge is-flex is-align-items-center" :href="'/user/'+ id">
    <figure class="image is-32x32 mr-2 is-flex-shrink-0"><img class="is-rounded" :src="user.oauth['picture']"></figure>
    {{ user.profile.badge_name }}
</a>
`
    Vue.component('user-badge', {
        template: tpl,
        props: {
            id: {
                type: String,
                required: true
            },
            users: {
                type: Object,
                required: true
            }
        },
        computed: {
            user () {
                return this.users[this.id]
            }
        }
    })
})()

