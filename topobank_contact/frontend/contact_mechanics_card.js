import {createApp} from 'vue';
import ContactMechanicsCard from './ContactMechanicsCard.vue';

export function createCardApp(el, props) {
    let app = createApp(ContactMechanicsCard, props);
    app.mount(el);
    return app;
}
