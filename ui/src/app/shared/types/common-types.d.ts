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

export interface ApiCollectionResponse<T /** the type of collection item.*/> {
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

export interface SortBy {
  index: number;
  property: string;
  direction: SortByDirection;
}

export type User = {
  first_name?: string;
  last_name?: string;
  email: string;
};

export interface ProjectType {
  id: string;
  name?: string;
  description?: string;
  scm_type?: string;
  scm_token?: string;
  created_at?: string;
  modified_at?: string;
  url?: string;
  status?: string;
  type?: string;
  revision?: string;
  vars?: [{ id: string; name: string }];
  rulesets?: [{ id: string; name: string }];
  inventories?: [{ id: string; name: string }];
  playbooks?: [{ id: string; name: string }];
}

export interface TabItemType {
  eventKey: number;
  title: string | JSXElement;
  name: string;
}
