import { createGlobalStyle } from 'styled-components';

/**
 * Use direct css imports for FCE components
 * This will save some bundle size
 */
const GlobalStyle = createGlobalStyle`
.disabled-link {
  pointer-events: none
}

h2.pf-c-nav__section-title {
  font-size: 18px;
  font-weight: var(--pf-global--FontWeight--semi-bold);
}

.icon-danger-fill {
  fill: var(--pf-global--danger-color--100)
}

.bottom-pagination-container {
  width: 100%
}

.global-primary-background {
  background-color: var(--pf-global--BackgroundColor--100)
}

.full-height {
  min-height: 100%;
}

.content-layout {
  display: flex;
  flex-direction: column;
}
`;

export default GlobalStyle;
