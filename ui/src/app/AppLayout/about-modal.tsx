import * as React from 'react';
import {
  AboutModal,
  TextContent,
  TextList,
  TextListItem,
  TextListItemVariants,
  TextListVariants
} from '@patternfly/react-core';
import Logo from '../../assets/images/logo-masthead.svg';
import { detect } from 'detect-browser';

interface IProps {
  isOpen: boolean;
  user: {email: string};
  trademark: string;
  brandImageSrc: string;
  onClose: () => void;
  brandImageAlt: string;
  productName: string;
}

interface IState {
  applicationInfo: { server_version: string };
}

export const AboutModalWindow = (props: IProps) => {
  const { isOpen, onClose, user, brandImageAlt, productName } = props;
  const browser = detect();
  return (
    <AboutModal
      isOpen={isOpen}
      trademark=""
      brandImageSrc={Logo}
      onClose={onClose}
      brandImageAlt={brandImageAlt}
      productName={productName}
    >
      <TextContent>
        <TextList component={TextListVariants.dl}>
          <TextListItem component={TextListItemVariants.dt}>
            {`User`}
          </TextListItem>
          <TextListItem component={TextListItemVariants.dd}>
            {user?.email}
          </TextListItem>
          <TextListItem component={TextListItemVariants.dt}>
            {`Browser Version`}
          </TextListItem>
          <TextListItem component={TextListItemVariants.dd}>
            {browser?.name + ' ' + browser?.version}
          </TextListItem>
          <TextListItem component={TextListItemVariants.dt}>
            {`Browser OS`}
          </TextListItem>
          <TextListItem component={TextListItemVariants.dd}>
            {browser?.os}
          </TextListItem>
        </TextList>
      </TextContent>
    </AboutModal>
  );
};
