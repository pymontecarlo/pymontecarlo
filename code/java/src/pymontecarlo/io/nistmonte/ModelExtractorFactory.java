package pymontecarlo.io.nistmonte;

import gov.nist.microanalysis.EPQLibrary.AbsoluteIonizationCrossSection;
import gov.nist.microanalysis.EPQLibrary.AlgorithmClass;
import gov.nist.microanalysis.EPQLibrary.BetheElectronEnergyLoss;
import gov.nist.microanalysis.EPQLibrary.CzyzewskiMottScatteringAngle;
import gov.nist.microanalysis.EPQLibrary.IonizationCrossSection;
import gov.nist.microanalysis.EPQLibrary.MassAbsorptionCoefficient;
import gov.nist.microanalysis.EPQLibrary.MeanIonizationPotential;
import gov.nist.microanalysis.EPQLibrary.NISTMottScatteringAngle;
import gov.nist.microanalysis.EPQLibrary.ProportionalIonizationCrossSection;
import gov.nist.microanalysis.EPQLibrary.RandomizedScatterFactory;
import gov.nist.microanalysis.EPQLibrary.ScreenedRutherfordScatteringAngle;
import gov.nist.microanalysis.EPQLibrary.Strategy;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;

/**
 * Factory of model extractors.
 * 
 * @author ppinard
 */
public class ModelExtractorFactory implements ExtractorFactory<ModelExtractor> {

    /**
     * Implementation of the <code>ModelExtractor</code> interface.
     * 
     * @author ppinard
     * @param <T>
     *            <code>AlgorithmClass</code> corresponding to the model type
     */
    private static class ModelExtractorImpl<T extends AlgorithmClass>
            implements ModelExtractor {

        /** Model type. */
        private final String type;

        /** Class of all algorithms. */
        private final Class<T> clasz;

        /** Look-up table for the algorithm class. */
        private final Map<String, T> lut;

        /** XML tag. */
        private static final String TAG = "pymontecarlo.input.base.model.Model";



        /**
         * Creates a new <code>ModelExtractor</code>.
         * 
         * @param type
         *            type of the models
         * @param clasz
         *            <code>AlgorithmClass</code> corresponding to the model
         *            type
         * @param lut
         *            look-up table linking the model name with the
         *            <code>AlgorithmClass</code>
         */
        public ModelExtractorImpl(String type, Class<T> clasz,
                Map<String, ? extends T> lut) {
            this.type = type;
            this.clasz = clasz;

            this.lut = new HashMap<String, T>();
            for (Entry<String, ? extends T> entry : lut.entrySet())
                this.lut.put(entry.getKey().toLowerCase(), entry.getValue());
        }



        @Override
        public boolean canExtract(Element element) {
            return element.getName().equals(TAG)
                    && JDomUtils.getStringFromAttribute(element, "type")
                            .equals(type);
        }



        @Override
        public void extract(Element modelElement, Strategy strategy)
                throws IOException {
            String name =
                    JDomUtils.getStringFromAttribute(modelElement, "name");
            AlgorithmClass algorithm = lut.get(name.toLowerCase());
            if (algorithm == null)
                throw new IOException("Unknown model (" + name + ") for type ("
                        + type + ")");

            strategy.addAlgorithm(clasz, algorithm);
        }
    }

    /** Model extractor for elastic cross section. */
    public static final ModelExtractor ELASTIC_CROSS_SECTION;

    /** Model extractor for ionization cross section. */
    public static final ModelExtractor IONIZATION_CROSS_SECTION;

    /** Model extractor for ionization potential. */
    public static final ModelExtractor IONIZATION_POTENTIAL;

    /** Model extractor for energy loss. */
    public static final ModelExtractor ENERGY_LOSS;

    /** Model extractor for mass absorption coefficient. */
    public static final ModelExtractor MASS_ABSORPTION_COEFFICIENT;



    @Override
    public List<ModelExtractor> getAllExtractors() {
        List<ModelExtractor> extractors = new ArrayList<ModelExtractor>();

        extractors.add(ELASTIC_CROSS_SECTION);
        extractors.add(IONIZATION_CROSS_SECTION);
        extractors.add(IONIZATION_POTENTIAL);
        extractors.add(ENERGY_LOSS);
        extractors.add(MASS_ABSORPTION_COEFFICIENT);

        return Collections.unmodifiableList(extractors);
    }

    static {
        // Elastic cross section
        HashMap<String, RandomizedScatterFactory> elasticCrossSectionLUT =
                new HashMap<String, RandomizedScatterFactory>();
        elasticCrossSectionLUT.put("Mott by interpolation (Czyzewski)",
                CzyzewskiMottScatteringAngle.Factory);
        elasticCrossSectionLUT.put("Rutherford",
                ScreenedRutherfordScatteringAngle.Factory);
        elasticCrossSectionLUT.put("ELSEPA", NISTMottScatteringAngle.Factory);

        ELASTIC_CROSS_SECTION =
                new ModelExtractorImpl<RandomizedScatterFactory>(
                        "elastic cross section",
                        RandomizedScatterFactory.class, elasticCrossSectionLUT);

        // Ionization cross section
        HashMap<String, IonizationCrossSection> ionizationCrossSectionLUT =
                new HashMap<String, IonizationCrossSection>();
        ionizationCrossSectionLUT.put("Pouchou 1986",
                ProportionalIonizationCrossSection.Pouchou86);
        ionizationCrossSectionLUT.put("Dijkstra and Heijliger 1998 (PROZA96)",
                ProportionalIonizationCrossSection.Proza96);
        ionizationCrossSectionLUT.put("Casnati 1982",
                AbsoluteIonizationCrossSection.Casnati82);
        ionizationCrossSectionLUT.put("Bote and Salvat 2008",
                AbsoluteIonizationCrossSection.BoteSalvat2008);

        IONIZATION_CROSS_SECTION =
                new ModelExtractorImpl<IonizationCrossSection>(
                        "ionization cross section",
                        IonizationCrossSection.class, ionizationCrossSectionLUT);

        // Ionization potential
        HashMap<String, MeanIonizationPotential> ionizationPotentialLUT =
                new HashMap<String, MeanIonizationPotential>();
        ionizationPotentialLUT.put("Berger & Seltzer 1964",
                MeanIonizationPotential.Berger64);
        ionizationPotentialLUT.put("Berger & Seltzer 1983",
                MeanIonizationPotential.Berger83);
        ionizationPotentialLUT.put("Berger & Seltzer 1983 (CITZAF)",
                MeanIonizationPotential.BergerAndSeltzerCITZAF);
        ionizationPotentialLUT.put("Zeller 1975",
                MeanIonizationPotential.Zeller75);
        ionizationPotentialLUT.put("Duncumb & DeCasa 1969",
                MeanIonizationPotential.Duncumb69);
        ionizationPotentialLUT.put("Heinrich & Yakowitz 1970",
                MeanIonizationPotential.Heinrich70);
        ionizationPotentialLUT.put("Springer 1967",
                MeanIonizationPotential.Springer67);
        ionizationPotentialLUT.put("Wilson 1941",
                MeanIonizationPotential.Wilson41);
        ionizationPotentialLUT.put("Bloch 1933",
                MeanIonizationPotential.Bloch33);
        ionizationPotentialLUT.put("Sternheimer 1964",
                MeanIonizationPotential.Sternheimer64);

        IONIZATION_POTENTIAL =
                new ModelExtractorImpl<MeanIonizationPotential>(
                        "ionization potential", MeanIonizationPotential.class,
                        ionizationPotentialLUT);

        // Energy loss
        HashMap<String, BetheElectronEnergyLoss> energyLossLUT =
                new HashMap<String, BetheElectronEnergyLoss>();
        energyLossLUT
                .put("Bethe 1930", BetheElectronEnergyLoss.Bethe1930Strict);
        energyLossLUT.put("Modified Bethe 1930",
                BetheElectronEnergyLoss.Bethe1930);
        energyLossLUT.put("Joy and Luo 1989",
                BetheElectronEnergyLoss.JoyLuo1989);

        ENERGY_LOSS =
                new ModelExtractorImpl<BetheElectronEnergyLoss>("energy loss",
                        BetheElectronEnergyLoss.class, energyLossLUT);

        // Mass absorption coefficient
        HashMap<String, MassAbsorptionCoefficient> massAbsorptionCoefficientLUT =
                new HashMap<String, MassAbsorptionCoefficient>();
        massAbsorptionCoefficientLUT.put("Ruste 1979",
                MassAbsorptionCoefficient.Ruste79);
        massAbsorptionCoefficientLUT.put("Pouchou and Pichoir 1991",
                MassAbsorptionCoefficient.Pouchou1991);
        massAbsorptionCoefficientLUT.put("Pouchou and Pichoir 1988",
                MassAbsorptionCoefficient.PouchouPichoir88);
        massAbsorptionCoefficientLUT.put("Henke 1982",
                MassAbsorptionCoefficient.Henke82);
        massAbsorptionCoefficientLUT.put("Henke 1993",
                MassAbsorptionCoefficient.Henke1993);
        massAbsorptionCoefficientLUT.put(
                "Bastin and Heijligers 1985, 1988, 1989",
                MassAbsorptionCoefficient.BastinHeijligers89);
        massAbsorptionCoefficientLUT.put("Heinrich IXCOM 11 (DTSA)",
                MassAbsorptionCoefficient.HeinrichDtsa);
        massAbsorptionCoefficientLUT.put("Heinrich IXCOM 11",
                MassAbsorptionCoefficient.Heinrich86);
        massAbsorptionCoefficientLUT.put("NIST-Chantler 2005",
                MassAbsorptionCoefficient.Chantler2005);
        massAbsorptionCoefficientLUT.put("DTSA CitZAF",
                MassAbsorptionCoefficient.DTSA_CitZAF);
        massAbsorptionCoefficientLUT.put("No MAC",
                MassAbsorptionCoefficient.Null);

        MASS_ABSORPTION_COEFFICIENT =
                new ModelExtractorImpl<MassAbsorptionCoefficient>(
                        "mass absorption coefficient",
                        MassAbsorptionCoefficient.class,
                        massAbsorptionCoefficientLUT);
    }

}
