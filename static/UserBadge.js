(function () {
    const tpl = /* html */`
<a class="is-flex is-align-items-center" :href="'/user/'+ id">
    <figure class="image is-32x32 mr-2"><img class="is-rounded" :src="user.oauth['picture']"></figure>
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

