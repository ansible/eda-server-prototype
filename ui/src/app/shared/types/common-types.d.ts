import { ReactNode } from 'react';
import { MessageDescriptor } from 'react-intl';
import { SortByDirection } from '@patternfly/react-table';

export interface StringObject {
  [key: string]: string;
}

export interface AnyObject {
  [key: string]: any;
}

export interface ApiMetadata extends AnyObject {
  count?: number;
  limit?: number;
  offset?: number;
}

export interface ApiCollectionResponse<
  T /** he type of collection item.*/
  > {
  data: T[];
  meta: ApiMetadata;
}

export interface ActionNotification {
  fulfilled?: AnyObject;
  pending?: AnyObject;
  rejected?: AnyObject;
}

export type NotificationPayload =
  | {
  type: string;
  payload: {
    dismissable: boolean;
    variant: string;
    title: string;
    description: string;
  };
}
  | {
  type: string;
  payload: any;
};

export type FormatMessage = (
  message: MessageDescriptor,
  values?: AnyObject
) => ReactNode;

export interface SortBy {
  index: number;
  property: string;
  direction: SortByDirection;
}

export type User = {
  first_name?: string,
  last_name?: string,
  email: string
};

