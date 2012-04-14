package pymontecarlo.program.nistmonte.io;

import static org.junit.Assert.assertEquals;
import gov.nist.microanalysis.EPQLibrary.AbsoluteIonizationCrossSection;
import gov.nist.microanalysis.EPQLibrary.AlgorithmClass;
import gov.nist.microanalysis.EPQLibrary.BetheElectronEnergyLoss;
import gov.nist.microanalysis.EPQLibrary.IonizationCrossSection;
import gov.nist.microanalysis.EPQLibrary.MassAbsorptionCoefficient;
import gov.nist.microanalysis.EPQLibrary.MeanIonizationPotential;
import gov.nist.microanalysis.EPQLibrary.NISTMottScatteringAngle;
import gov.nist.microanalysis.EPQLibrary.RandomizedScatterFactory;
import gov.nist.microanalysis.EPQLibrary.Strategy;

import java.io.IOException;

import org.jdom.Element;
import org.junit.Before;
import org.junit.Test;

public class ModelExtractorFactoryTest {

    private Strategy strategy;



    @Before
    public void setUp() throws Exception {
        strategy = new Strategy();
    }



    public static Element createElasticCrossSectionModelElement() {
        Element element = new Element("model");

        element.setAttribute("type", "elastic cross section");
        element.setAttribute("name", "ELSEPA");

        return element;
    }



    @Test
    public void testELASTIC_CROSS_SECTION() throws IOException {
        // XML element
        Element element = createElasticCrossSectionModelElement();

        // Extrator
        ModelExtractor extractor = ModelExtractorFactory.ELASTIC_CROSS_SECTION;
        extractor.extract(element, strategy);

        // Test
        extractor.canExtract(element);

        AlgorithmClass alg =
                strategy.getAlgorithm(RandomizedScatterFactory.class);
        assertEquals(NISTMottScatteringAngle.Factory, alg);
    }



    public static Element createIonizationCrossSectionModelElement() {
        Element element = new Element("model");

        element.setAttribute("type", "ionization cross section");
        element.setAttribute("name", "Bote and Salvat 2008");

        return element;
    }



    @Test
    public void testIONIZATION_CROSS_SECTION() throws IOException {
        // XML element
        Element element = createIonizationCrossSectionModelElement();

        // Extrator
        ModelExtractor extractor =
                ModelExtractorFactory.IONIZATION_CROSS_SECTION;
        extractor.extract(element, strategy);

        // Test
        extractor.canExtract(element);

        AlgorithmClass alg =
                strategy.getAlgorithm(IonizationCrossSection.class);
        assertEquals(AbsoluteIonizationCrossSection.BoteSalvat2008, alg);
    }



    public static Element createIonizationPotentialModelElement() {
        Element element = new Element("model");

        element.setAttribute("type", "ionization potential");
        element.setAttribute("name", "Sternheimer 1964");

        return element;
    }



    @Test
    public void testIONIZATION_POTENTIAL() throws IOException {
        // XML element
        Element element = createIonizationPotentialModelElement();

        // Extrator
        ModelExtractor extractor = ModelExtractorFactory.IONIZATION_POTENTIAL;
        extractor.extract(element, strategy);

        // Test
        extractor.canExtract(element);

        AlgorithmClass alg =
                strategy.getAlgorithm(MeanIonizationPotential.class);
        assertEquals(MeanIonizationPotential.Sternheimer64, alg);
    }



    public static Element createEnergyLossModelElement() {
        Element element = new Element("model");

        element.setAttribute("type", "energy loss");
        element.setAttribute("name", "Joy and Luo 1989");

        return element;
    }



    @Test
    public void testENERGY_LOSS() throws IOException {
        // XML element
        Element element = createEnergyLossModelElement();

        // Extrator
        ModelExtractor extractor = ModelExtractorFactory.ENERGY_LOSS;
        extractor.extract(element, strategy);

        // Test
        extractor.canExtract(element);

        AlgorithmClass alg =
                strategy.getAlgorithm(BetheElectronEnergyLoss.class);
        assertEquals(BetheElectronEnergyLoss.JoyLuo1989, alg);
    }



    public static Element createMassAbsorptionCoefficientModelElement() {
        Element element = new Element("model");

        element.setAttribute("type", "mass absorption coefficient");
        element.setAttribute("name", "No MAC");

        return element;
    }



    @Test
    public void testMASS_ABSORPTION_COEFFICIENT() throws IOException {
        // XML element
        Element element = createMassAbsorptionCoefficientModelElement();

        // Extrator
        ModelExtractor extractor =
                ModelExtractorFactory.MASS_ABSORPTION_COEFFICIENT;
        extractor.extract(element, strategy);

        // Test
        extractor.canExtract(element);

        AlgorithmClass alg =
                strategy.getAlgorithm(MassAbsorptionCoefficient.class);
        assertEquals(MassAbsorptionCoefficient.Null, alg);
    }
}
