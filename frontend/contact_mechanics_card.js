import {createApp} from 'vue';
import ContactMechanicsCard from './ContactMechanicsCard.vue';

/**
 * Event bus for initiating DZI download
 */
import mitt from 'mitt';

const eventHub = mitt();

export function createCardApp(el, csrfToken, props) {
    let app = createApp(ContactMechanicsCard, props);
    app.provide('csrfToken', csrfToken);
    app.provide('eventHub', eventHub);
    app.mount(el);
    return app;
}
