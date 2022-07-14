import * as React from 'react';
import SmallLogoImage from '../../assets/images/logo-masthead.svg';

interface IProps {
  alt: string;
}

export class SmallLogo extends React.Component<IProps> {
  render() {
    return (
      <img
        style={{ height: '50px' }}
        src={SmallLogoImage}
        alt={this.props.alt}
      />
    );
  }
}
