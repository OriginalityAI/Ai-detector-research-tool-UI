import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faArrowRight,
  faCheck,
  faCopy,
  faMagicWandSparkles,
  faPenToSquare,
  faTurnDown,
  faUpload,
  faDownload,
  faCircleQuestion,
  faArrowDown,
  faArrowUp
} from '@fortawesome/free-solid-svg-icons'
import 'vuetify/styles'
import './styles/global.css'
import vuetify from './plugins/vuetify'

library.add(
  faPenToSquare,
  faCopy,
  faMagicWandSparkles,
  faCheck,
  faArrowRight,
  faTurnDown,
  faUpload,
  faDownload,
  faCircleQuestion,
  faArrowDown,
  faArrowUp
)

createApp(App)
  .use(vuetify)
  .use(createPinia())
  .component('font-awesome-icon', FontAwesomeIcon)
  .mount('#app')
