package pymontecarlo.io.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.GaussianFWHMBeam;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.ElectronGun;
import gov.nist.microanalysis.NISTMonte.PencilBeam;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;

/**
 * Factory of beam extractors.
 * 
 * @author ppinard
 */
public class BeamExtractorFactory implements ExtractorFactory<BeamExtractor> {

    /** Extractor for a <code>GaussianFWHMBeam</code>. */
    public static final BeamExtractor GAUSSIAN_FWHM =
            new AbstractBeamExtractor(
                    "pymontecarlo.input.base.beam.GaussianBeam") {

                @Override
                public ElectronGun extract(Element beamImplElement)
                        throws IOException, EPQException {
                    double diameter =
                            JDomUtils.getDoubleFromAttribute(beamImplElement,
                                    "diameter");
                    GaussianFWHMBeam beam = new GaussianFWHMBeam(diameter);

                    extractBeamEnergy(beamImplElement, beam);
                    extractCenter(beamImplElement, beam);
                    extractDirection(beamImplElement, beam);

                    return beam;
                }
            };

    /** Extractor for a <code>PencilBeam</code>. */
    public static final BeamExtractor PENCIL = new AbstractBeamExtractor(
            "pymontecarlo.input.base.beam.PencilBeam") {

        @Override
        public ElectronGun extract(Element beamImplElement) throws IOException,
                EPQException {
            PencilBeam beam = new PencilBeam();

            extractBeamEnergy(beamImplElement, beam);
            extractCenter(beamImplElement, beam);
            extractDirection(beamImplElement, beam);

            return beam;
        }
    };



    @Override
    public List<BeamExtractor> getAllExtractors() {
        List<BeamExtractor> extractors = new ArrayList<BeamExtractor>();

        extractors.add(PENCIL);
        extractors.add(GAUSSIAN_FWHM);

        return Collections.unmodifiableList(extractors);
    }
}
