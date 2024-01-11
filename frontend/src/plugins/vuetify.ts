import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import { fa } from 'vuetify/iconsets/fa'

//custom theme
const OriginalityTheme = {
  dark: false,
  colors: {
    primary: '#7859FF',
    secondary: '#5A4D8E',
    accent: '#FFFFFF',
    success: '#689F38',
    info: '#2B2154',
    error: '#D32F2F',
    warning: '#FFBB59'
  }
}

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'OriginalityTheme',
    themes: {
      OriginalityTheme
    }
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
      fa
    }
  }
})

export default vuetify