/**
 * @jest-environment jsdom
 */
import React from 'react'
import { configure, mount, render, shallow } from 'enzyme';
import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import fetchMock from "jest-fetch-mock";

fetchMock.enableMocks();


/**
 * mock fetch
 */
import 'whatwg-fetch';

/**
 * mock react-intl in tests
 */
// eslint-disable-next-line no-undef
jest.mock('react-intl', () => {
  const reactIntl = jest.genMockFromModule('react-intl');
  const intl = reactIntl.createIntl({
    locale: 'en'
  });

  return {
    ...reactIntl,
    useIntl: () => intl
  };
});

configure({ adapter: new Adapter() });

global.shallow = shallow;
global.render = render;
global.mount = mount;
global.React = React;

/**
 * Setup JSDOM
 */
global.SVGPathElement = function() {};

global.MutationObserver = class {
  constructor(callback) {}
  disconnect() {}
  observe(element, initObject) {}
};

// prepare root element
const root = document.createElement('div');
root.id = 'root';
document.body.appendChild(root);
Element.prototype.scrollTo = () => {};

