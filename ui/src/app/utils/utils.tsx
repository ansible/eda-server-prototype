import React from 'react';
import { TabItemType } from '@app/shared/types/common-types';
import { CheckCircleIcon, ExclamationCircleIcon, ExclamationTriangleIcon } from '@patternfly/react-icons';
import { useEffect, useRef } from 'react';
import { Label } from '@patternfly/react-core';
import sharedMessages from '../messages/shared.messages';

export function accessibleRouteChangeHandler() {
  return window.setTimeout(() => {
    const mainContainer = document.getElementById('primary-app-container');
    if (mainContainer) {
      mainContainer.focus();
    }
  }, 50);
}

export async function removeData(url = '') {
  const response = await fetch(url, {
    method: 'DELETE',
    mode: 'cors',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
  });
}

export async function postData(url = '', data = {}) {
  const response = await fetch(url, {
    method: 'POST',
    mode: 'cors',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
    body: JSON.stringify(data),
  });
  if (response.ok) {
    return response.json();
  }
  throw new Error(`${response?.status} - ${response?.statusText}`);
}

export async function patchData(url = '', data = {}) {
  const response = await fetch(url, {
    method: 'PATCH',
    mode: 'cors',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
    },
    redirect: 'follow',
    referrerPolicy: 'no-referrer',
    body: JSON.stringify(data),
  });
  if (response.ok) {
    return response.json();
  }
  throw new Error(`${response?.status} - ${response?.statusText}`);
}

export function getServer() {
  return window.location.hostname + ':' + window.location.port;
}

export const getTabFromPath = (tabs: TabItemType[], path: string): string | undefined => {
  const currentTab = tabs.find((tabItem) => tabItem.name.split('/').pop() === path.split('/').pop());
  return currentTab?.title;
};

export const usePrevious = <T extends unknown>(value: T): T | undefined => {
  const ref = useRef<T>();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
};

export const statusLabel = ({ text, intl }) => {
  switch (text) {
    case 'failed':
      return (
        <Label href="#filled" icon={<ExclamationCircleIcon />} color={'red'}>
          {intl.formatMessage(sharedMessages.failed)}
        </Label>
      );
    case 'ok':
      return (
        <Label href="#filled" icon={<CheckCircleIcon />} color={'green'}>
          {intl.formatMessage(sharedMessages.ok)}
        </Label>
      );
    case 'success':
      return (
        <Label href="#filled" icon={<CheckCircleIcon />} color={'green'}>
          {intl.formatMessage(sharedMessages.success)}
        </Label>
      );
    case 'successful':
      return (
        <Label href="#filled" icon={<CheckCircleIcon />} color={'green'}>
          {intl.formatMessage(sharedMessages.successful)}
        </Label>
      );
    case 'error':
      return (
        <Label href="#filled" icon={<ExclamationCircleIcon />} color={'red'}>
          {intl.formatMessage(sharedMessages.error)}
        </Label>
      );
    case 'skipped':
      return (
        <Label href={'#filled'} color={'grey'}>
          {intl.formatMessage(sharedMessages.skipped)}
        </Label>
      );
    case 'unreachable':
      return (
        <Label href="#filled" icon={<ExclamationTriangleIcon />} color={'orange'}>
          {intl.formatMessage(sharedMessages.unreachable)}
        </Label>
      );
    case 'no remaining':
      return (
        <Label href={'#filled'} color={'grey'}>
          {' '}
          {intl.formatMessage(sharedMessages.no_remaining)}
        </Label>
      );
    case 'polling':
      return (
        <Label href={'#filled'} color={'grey'}>
          {' '}
          {intl.formatMessage(sharedMessages.polling)}
        </Label>
      );
    case 'async ok':
      return (
        <Label href="#filled" icon={<CheckCircleIcon />} color={'green'}>
          {intl.formatMessage(sharedMessages.async_ok)}
        </Label>
      );
    case 'async failure':
      return (
        <Label href="#filled" icon={<ExclamationCircleIcon />} color={'red'}>
          {intl.formatMessage(sharedMessages.async_failure)}
        </Label>
      );
    case 'retry':
      return (
        <Label href="#filled" icon={<ExclamationCircleIcon />} color={'blue'}>
          {intl.formatMessage(sharedMessages.retry)}
        </Label>
      );
    case 'no hosts':
      return (
        <Label href={'#filled'} color={'grey'}>
          {intl.formatMessage(sharedMessages.no_hosts)}
        </Label>
      );
    case 'no_matched':
      return (
        <Label href="#filled" color={'grey'}>
          {intl.formatMessage(sharedMessages.no_matched)}
        </Label>
      );
    default:
      return <Label color={'orange'}>Unknown</Label>;
  }
};
