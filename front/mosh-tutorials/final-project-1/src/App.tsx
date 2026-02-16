import { Grid, GridItem } from "@chakra-ui/react";
import { NavBar } from "./components/NavBar";
import { GameGrid } from "./components/GameGrid";

function App() {
  return (
    <Grid
      templateAreas={{
        base: `"nav" "main"`,
        lg: `"nav nav"
             "aside main"`,
      }}
    >
      <GridItem area="nav">
        <NavBar />
      </GridItem>
      <GridItem area="aside" bg="gold" hideBelow="lg">
        Aside
      </GridItem>
      <GridItem area="main" bg="dark">
        <GameGrid />
      </GridItem>
    </Grid>
  );
}

export default App;
