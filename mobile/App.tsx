import React from 'react';
import {StatusBar} from 'react-native';
import {AppNavigator} from './src/navigation/AppNavigator';
import {colors} from './src/theme';

function App(): React.JSX.Element {
  return (
    <>
      <StatusBar
        barStyle="dark-content"
        backgroundColor={colors.bg}
      />
      <AppNavigator />
    </>
  );
}

export default App;
