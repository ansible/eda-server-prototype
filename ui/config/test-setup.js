/**
 * @jest-environment jsdom
 */
import React from 'react';
import { configure, mount, render, shallow } from 'enzyme';
import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import fetchMock from 'jest-fetch-mock';

/**
 * mock fetch
 */
import 'whatwg-fetch';

import reactIntl from 'react-intl';
import 'jest-canvas-mock';

/**
 * mock react-intl in tests
 *
 */
fetchMock.enableMocks();

configure({ adapter: new Adapter() });

global.shallow = shallow;
global.render = render;
global.mount = mount;
global.React = React;
global.fetchMock = fetchMock;

/**
 * Setup JSDOM
 */
global.SVGPathElement = function () {};

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
